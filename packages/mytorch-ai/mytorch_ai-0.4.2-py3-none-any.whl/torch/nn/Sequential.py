###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from torch.nn.Module import Module
from proxies.mytorch.nn.sequential_proxy import SequentialProxy
from proxies.mytorch.nn.lstm_proxy import LSTMProxy
from proxies.mytorch.nn.layers_proxy import LinearProxy, ReLUProxy, FlattenProxy
from proxies.mytorch.nn.layers_proxy import LinearProxy, ReLUProxy, FlattenProxy, SigmoidProxy
import torch.nn as nn

class Sequential(Module):
    def __init__(self, *args):
        super().__init__(uuid="0000")
        layer_proxies = [self._convert_to_proxy(layer) for layer in args]
        self.proxy = SequentialProxy(*layer_proxies)
        self.uuid = self.proxy.create_sequential_on_server() 
        self.set_uuid(self.uuid)

    def forward(self, input_data):
        return super().forward(input_data)

    def _convert_to_proxy(self, layer):
        if isinstance(layer, nn.Linear):
            return LinearProxy(layer.in_features, layer.out_features)
        elif isinstance(layer, nn.ReLU):
            return ReLUProxy()
        elif isinstance(layer, nn.Flatten):
            return FlattenProxy()

        elif isinstance(layer, nn.LSTM):
            return LSTMProxy()
        elif isinstance(layer, nn.Sigmoid):
            return SigmoidProxy()
        else:
            raise NotImplementedError(f"Layer type {type(layer)} is not supported.")

