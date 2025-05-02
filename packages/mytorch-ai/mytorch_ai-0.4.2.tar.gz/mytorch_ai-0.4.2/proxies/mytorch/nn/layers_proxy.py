###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from enum import Enum, auto
from torch.Tensor import Tensor
from proxies.base_proxy import BaseProxy
from utils.logger import Logger
from connection_utils.server_connection import ServerConnection, wrap_with_error_handler

############################################
# LayerType enum
############################################
class LayerType(Enum):
    LINEAR = auto()
    RELU = auto()
    FLATTEN = auto()
    SIGMOID = auto()
    MSELOSS = auto()
    # Add other layer types as needed

class LayerProxy (BaseProxy):
    def __init__(self, layer_type: LayerType, **params):
        self.layer_type = layer_type
        self.params = params
        self.logger = Logger.get_logger()
        self.channel = ServerConnection.get_active_connection()

    def print(self):
        print(f"Layer type: {self.layer_type.name}, Params: {self.params}")

    def describe(self):
        return f"Layer type: {self.layer_type.name}, Params: {self.params}"

class LinearProxy(LayerProxy):
    def __init__(self, in_features, out_features):
        super().__init__(LayerType.LINEAR, in_features=in_features, out_features=out_features)

class ReLUProxy(LayerProxy):
    def __init__(self):
        super().__init__(LayerType.RELU)

    def forward(self, tensor):
        """Calls ReLU on the server via generic_call."""
        uuid, shape, dtype = self.generic_call("torch.nn", 
                                               "ReLU", 
                                               tensor.uuid,
                                               call_type="forward")
        return Tensor(uuid, shape, dtype)
    
class FlattenProxy(LayerProxy):
    def __init__(self):
        super().__init__(LayerType.FLATTEN)

class SigmoidProxy(LayerProxy):
    def __init__(self):
        super().__init__(LayerType.SIGMOID)
    
    def forward(self, tensor):
        uuid, shape, dtype = self.generic_call("torch", 
                                               "sigmoid", 
                                               tensor.uuid, 
                                               call_type="function")
        return Tensor(uuid, shape, dtype)

class MSELossProxy(LayerProxy):
    def __init__(self, size_average=None, reduce=None, reduction: str = "mean"):
        super().__init__(LayerType.MSELOSS)

    def forward(self, input: Tensor, output: Tensor):
        """Calls ReLU on the server via generic_call."""
        uuid, shape, dtype = self.generic_call("torch.nn", 
                                               "MSELoss", 
                                               input.uuid, 
                                               output.uuid,
                                               call_type="forward")
        return Tensor(uuid, shape, dtype)