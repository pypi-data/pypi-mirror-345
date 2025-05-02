###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from proxies.mytorch.nn.layers_proxy import FlattenProxy

class Flatten:
    def __init__(self):
        self.proxy = FlattenProxy()