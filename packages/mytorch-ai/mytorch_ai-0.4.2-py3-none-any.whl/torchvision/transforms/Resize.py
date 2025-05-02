###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from .Transformer import Transformer
from proxies.mytorchvision.transforms.ResizeProxy import ResizeProxy

class Resize (Transformer):
    def __init__(self, size: int):
        super().__init__()
        self.size = size
        self.proxy = ResizeProxy(size)
        self.uuid = self.proxy.createTransformOnServer()

