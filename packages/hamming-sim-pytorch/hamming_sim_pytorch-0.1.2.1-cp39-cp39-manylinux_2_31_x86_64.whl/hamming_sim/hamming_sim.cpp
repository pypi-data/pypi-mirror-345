#include <torch/extension.h>
#include <vector>
#include <immintrin.h>  // AVX2 intrinsics
#include <omp.h>        // OpenMP for Multi-threading

torch::Tensor quantized_1bit_tensor_similarity(torch::Tensor tensor1, torch::Tensor tensor2) {
    TORCH_CHECK(tensor1.dtype() == torch::kUInt8, "tensor1 must be of dtype uint8");
    TORCH_CHECK(tensor2.dtype() == torch::kUInt8, "tensor2 must be of dtype uint8");
    TORCH_CHECK(tensor1.size(1) == tensor2.size(1), "Both tensors must have the same last dimension");

    int64_t M = tensor1.size(0);
    int64_t N = tensor2.size(0);
    int64_t D = tensor1.size(1); // Number of bytes per row (D = bit length / 8)

    auto similarity = torch::empty({M, N}, torch::TensorOptions().dtype(torch::kFloat32));

    uint8_t* t1_ptr = tensor1.data_ptr<uint8_t>();
    uint8_t* t2_ptr = tensor2.data_ptr<uint8_t>();
    float* sim_ptr = similarity.data_ptr<float>();

    const float scale = 1.0f / (D * 8); // Normalize by total bits

    #pragma omp parallel for schedule(dynamic)
    for (int64_t i = 0; i < M; i++) {
        for (int64_t j = 0; j < N; j++) {
            int popcount_sum = 0;
            uint8_t* row1 = t1_ptr + i * D;
            uint8_t* row2 = t2_ptr + j * D;

            int64_t d = 0;

            for (; d <= D - 32; d += 32) { // Process 32 bytes per iteration
                __m256i a = _mm256_loadu_si256((__m256i*)(row1 + d));
                __m256i b = _mm256_loadu_si256((__m256i*)(row2 + d));
                __m256i xor_res = _mm256_xor_si256(a, b);

                // Compute popcount on 4 x 64-bit lanes
                popcount_sum += _mm_popcnt_u64(_mm256_extract_epi64(xor_res, 0));
                popcount_sum += _mm_popcnt_u64(_mm256_extract_epi64(xor_res, 1));
                popcount_sum += _mm_popcnt_u64(_mm256_extract_epi64(xor_res, 2));
                popcount_sum += _mm_popcnt_u64(_mm256_extract_epi64(xor_res, 3));
            }

            // Process remaining bytes (scalar popcount)
            for (; d < D; d++) {
                popcount_sum += __builtin_popcount(row1[d] ^ row2[d]);
            }

            // Compute similarity (1 - Hamming distance)
            sim_ptr[i * N + j] = 1.0f - (popcount_sum * scale);
        }
    }

    return similarity;
}

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
    m.def("quantized_1bit_tensor_similarity", &quantized_1bit_tensor_similarity, "Optimized 1-bit Tensor Similarity (AVX2, SIMD Popcount)");
}
