###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from .Transformer import Transformer
from proxies.mytorchvision.transforms.ComposeProxy import ComposeProxy

class Compose (Transformer):
    def __init__(self, transforms: list):
        super().__init__()
        self.transforms = transforms
        self.transform_uuids = [transform.uuid for transform in transforms]
        self.proxy = ComposeProxy(self.transform_uuids)
        self.uuid = self.proxy.createTransformOnServer()