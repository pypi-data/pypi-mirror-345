###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from proxies.mytorch.jit.jit_proxy import JitProxy
from torch.nn.Module import Module
from torch.Tensor import Tensor

def trace(model: Module, example_tensor: Tensor) -> Module:
    model_uuid = JitProxy().trace(model, example_tensor)
    module = Module(uuid=model_uuid)
    return module

def save(module: Module, path: str) -> None:
    JitProxy().save(module, path)

def load(path: str) -> Module:
    model_uuid = JitProxy().load(path)
    module = Module(uuid=model_uuid)
    return module