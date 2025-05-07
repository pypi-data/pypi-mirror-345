import torch

from hamming_sim import hamming_sim
from hamming_sim.utils import unpack_tensor

__all__ = ["quantized_1bit_tensor_similarity", "unpack_tensor"]


def quantized_1bit_tensor_similarity(
    tensor1: torch.Tensor, tensor2: torch.Tensor
) -> torch.Tensor:
    """
    The similarity between two 1-bit quantized tensors. The function is wrapper around the cpp extension.
    The tensors should be of type uint8, the cpp extension will assert this.

    :param tensor1: First quantized tensor of shape [M, D].
    :param tensor2: Second quantized tensor of shape [N, D].
    :return: The similarity between the two tensors of shape [M, N].
    """
    tensor1 = tensor1.contiguous()
    tensor2 = tensor2.contiguous()
    return hamming_sim.quantized_1bit_tensor_similarity(tensor1, tensor2)
