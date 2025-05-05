import os
import shutil

from pathlib import Path

from setuptools import Distribution
from torch.utils.cpp_extension import BuildExtension, CppExtension, include_paths


def build() -> None:
    build_dir = Path(__file__).parent.parent / "hamming_sim"
    ext_modules = [
        CppExtension(
            name="hamming_sim",
            sources=["hamming_sim/hamming_sim.cpp"],
            include_dirs=[include_paths()],  # Ensures PyTorch headers are included.
            extra_compile_args=["-O3", "-march=haswell", "-mavx2", "-fopenmp"],
            extra_link_args=["-ltorch", "-ltorch_cpu", "-lgomp"],
        ),
    ]
    distribution = Distribution(
        {
            "name": "hamming_sim",
            "ext_modules": ext_modules,
        }
    )

    cmd = BuildExtension(distribution)
    cmd.ensure_finalized()
    cmd.run()

    for output in cmd.get_outputs():
        output = Path(output)
        target_filename = build_dir / output.relative_to(cmd.build_lib)
        shutil.copyfile(output, target_filename)
        mode = os.stat(target_filename).st_mode
        mode |= (mode & 0o444) >> 2
        os.chmod(target_filename, mode)


if __name__ == "__main__":
    build()
