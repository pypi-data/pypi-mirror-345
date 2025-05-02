###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from .Transformer import Transformer
from proxies.mytorchvision.transforms.ToTensorProxy import ToTensorProxy

class ToTensor (Transformer):
    def __init__(self):
        super().__init__()
        self.proxy = ToTensorProxy()
        self.uuid = self.proxy.createTransformOnServer()

