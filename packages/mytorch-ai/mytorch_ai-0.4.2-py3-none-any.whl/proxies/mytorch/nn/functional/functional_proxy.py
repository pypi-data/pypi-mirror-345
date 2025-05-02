###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from gRPC_impl.mytorch.nn.functional import functional_pb2, functional_pb2_grpc
from torch.Tensor import Tensor
from utils.logger import Logger

class FunctionalProxy:
    def __init__(self):
        self.channel = ServerConnection.get_active_connection()
        self.stub = functional_pb2_grpc.FunctionalServiceStub(self.channel)
        self.logger = Logger.get_logger()
        self.uuid = None

    @wrap_with_error_handler
    def softmax(self, input: Tensor, dim: int) -> Tensor:
        request = functional_pb2.SoftmaxRequest(tensor_uuid=input.uuid, dim=dim)
        response = self.stub.softmax(request)
        return Tensor(response.uuid, response.shape, response.dtype)
    
    
    #@wrap_with_error_handler
    #def relu(self, input: Tensor, dim: int) -> Tensor:
    #    return self.generic_call("torch", "rand", *size) # TODO Make just ONE generic_call, currently many