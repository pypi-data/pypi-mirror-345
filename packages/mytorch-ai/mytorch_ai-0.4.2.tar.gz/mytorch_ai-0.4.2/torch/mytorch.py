###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from proxies.mytorch.mytorch_proxy import MyTorchProxy
from proxies.no_op import NoOpContextManager
from torch.Tensor import Tensor
from torch.device import device
import numpy as np
from typing import Dict, List
import json

def randn(*size: int) -> Tensor:
    size = list(size)
    return MyTorchProxy().randn(size)

def rand(*size: int) -> Tensor:
    size = list(size)
    return MyTorchProxy().rand(size)

def zeros(*size: int) -> Tensor:
    size = list(size)
    return MyTorchProxy().zeros(size)

def ones(*size: int) -> Tensor:
    size = list(size)
    return MyTorchProxy().ones(size)

def from_numpy(ndarray: np.ndarray) -> Tensor:
    # Implementation to request a tensor from the server
    return MyTorchProxy().from_numpy(ndarray)

def no_grad():
    return NoOpContextManager()

def max(tensor: Tensor, dim: int) -> tuple[Tensor, Tensor]:
    return MyTorchProxy().max(tensor, dim)

def repeat_interleave(tensor: Tensor, repeats: int, dim: int) -> Tensor:
    return MyTorchProxy().repeat_interleave(tensor, repeats, dim)

def unsqueeze(tensor: Tensor, dim: int) -> Tensor:
    return MyTorchProxy().unsqueeze(tensor, dim)

def arange(start, end, step) -> Tensor:
    # make sure stare, end, and step are floats
    start = float(start)
    end = float(end)
    step = float(step)
    return MyTorchProxy().arange(start, end, step)

def meshgrid(*tensors: Tensor, indexing: str = 'xy') -> tuple:
    tensor_uuids = [tensor.uuid for tensor in tensors]
    return MyTorchProxy().meshgrid(tensor_uuids, indexing)

def reshape(tensor: Tensor, shape: tuple) -> Tensor:
    return MyTorchProxy().reshape(tensor, shape)

def cat(tensors, dim: int) -> Tensor:
    return MyTorchProxy().cat(tensors, dim)

def argmax(tensor: Tensor, dim: int = None, keepdim: bool = False) -> Tensor:
    return MyTorchProxy().argmax(tensor, dim, keepdim)

def matmul(tensor1: Tensor, tensor2: Tensor) -> Tensor:
    return MyTorchProxy().matmul(tensor1, tensor2)

def load(file_path: str) -> Dict[str, Tensor]:
    return MyTorchProxy().load(file_path)

def save(state_dict: Dict[str, Tensor], file_path: str):
    return MyTorchProxy().save(state_dict, file_path)

def allclose(input: Tensor, other: Tensor, rtol: float = 1e-05, atol: float = 1e-08, equal_nan: bool = False) -> bool:
    return MyTorchProxy().allclose(input, other, rtol, atol, equal_nan)

def device(dev: str) -> device:
    return MyTorchProxy().device(dev)

def tanh(tensor: Tensor) -> Tensor:
    return MyTorchProxy().tanh(tensor)

def sigmoid(tensor: Tensor) -> Tensor:
    return MyTorchProxy().sigmoid(tensor)

def stack(tensors : List, dim: int = 0) -> Tensor:
    tensor_uuids = [tensor.uuid for tensor in tensors]
    return MyTorchProxy().stack( tensor_uuids, dim)

def mean(input, dim=None, keepdim=False, dtype=None, out=None) -> Tensor:
    # If the input tensor is empty, torch.mean() returns nan. 
    # This behavior is consistent with NumPy
    return MyTorchProxy().mean(input, dim, keepdim, dtype, out)

def randn_like(input: Tensor) -> Tensor:
    return randn(*input.size())

def equal(tensor1: Tensor, tensor2: Tensor) -> bool:
    return MyTorchProxy().equal(tensor1, tensor2)