###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from proxies.mytorch.nn.layers_proxy import LinearProxy

class Linear:
    def __init__(self, in_features, out_features):
        self.in_features = in_features
        self.out_features = out_features
        self.proxy = LinearProxy(in_features, out_features)