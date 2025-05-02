###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

"""
This proxy provides a proxy for the MyTorchService gRPC service.
It allows the client to call specified torch operations on the server via gRPC.
"""

from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from gRPC_impl.mytorch_neuronx import mytorch_neuronx_pb2_grpc, mytorch_neuronx_pb2
from utils.logger import Logger
from torch.Tensor import Tensor
from torch.nn.Module import Module

class CqtorchNeuronxProxy:

    def __init__(self):
        self.channel = ServerConnection.get_active_connection()
        self.stub = mytorch_neuronx_pb2_grpc.CqtorchNeuronxServiceStub(self.channel)
        self.logger = Logger.get_logger()

    @wrap_with_error_handler
    def trace(self, model: Module, example_inputs: tuple[Tensor, ...]) -> str:
        request = mytorch_neuronx_pb2.TraceRequest() # for type hinting later on
        # get the uuid of each tensor in example_inputs
        tensor_uuid_list = [tensor.uuid for tensor in example_inputs]
        request.model_uuid = model.uuid
        request.tensor_uuid_tuple.extend(tensor_uuid_list)
        response: mytorch_neuronx_pb2.TraceResponse = self.stub.trace(request)
        return response.model_uuid
