###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from .Transformer import Transformer
from proxies.mytorchvision.transforms.CenterCropProxy import CenterCropProxy

class CenterCrop (Transformer):
    def __init__(self, size: int):
        super().__init__()
        self.size = size
        self.proxy = CenterCropProxy(size)
        self.uuid = self.proxy.createTransformOnServer()

