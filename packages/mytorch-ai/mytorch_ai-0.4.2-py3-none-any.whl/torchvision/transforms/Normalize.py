###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from .Transformer import Transformer
from proxies.mytorchvision.transforms.NormalizeProxy import NormalizeProxy

class Normalize (Transformer):
    def __init__(self, mean: list, std: list):
        super().__init__()
        self.mean = mean
        self.std = std
        self.proxy = NormalizeProxy(mean, std)
        self.uuid = self.proxy.createTransformOnServer()
