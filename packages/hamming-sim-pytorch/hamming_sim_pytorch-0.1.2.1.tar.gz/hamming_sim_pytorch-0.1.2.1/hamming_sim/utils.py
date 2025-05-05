import torch


def unpack_tensor(tensor: torch.Tensor) -> torch.Tensor:
    """
    Unpack the 1 bit quantized tensor into the bits for each orginal value.
    :param tensor: The quantized tensor.
    :return: The unpacked tensor.
    """
    assert tensor.dtype == torch.uint8, "The tensor must be of type uint8."

    *N, _ = tensor.shape
    shifts = torch.tensor(
        list(range(0, 8, 1))[::-1], device=tensor.device, dtype=torch.int8
    )
    tensor = tensor.view(-1, 1)
    decoded = (tensor >> shifts) & 1
    return decoded.view(*N, -1)
