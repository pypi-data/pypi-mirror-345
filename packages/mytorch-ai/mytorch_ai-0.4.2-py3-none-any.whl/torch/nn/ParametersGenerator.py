###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from connection_utils.server_connection import ServerConnection
from gRPC_impl import shared_msg_types_pb2
from gRPC_impl.mytorch.nn import module_pb2_grpc
from utils.logger import Logger
from torch.Tensor import Tensor  

class ParametersGenerator:
    """
    Wraps a model UUID, and when iterated, fetches parameters from the server.
    BROKEN !!!
    """
    #def __init__(self, uuid: str):
    #    self.uuid = uuid
    #    self.channel = ServerConnection.get_active_connection()
    #    self.stub = module_pb2_grpc.ModuleServiceStub(self.channel)
    #    self.logger = Logger.get_logger()

    #def __iter__(self):
    #    # Get all parameters in a single gRPC call
    #    request = shared_msg_types_pb2.UUID(uuid=self.uuid)
    #    response = self.stub.GetParameters(request)

    #    # The response is a Parameters message with repeated GrpcTensor fields
    #    for grpc_tensor in response.parameters:
    #        yield Tensor(
    #            uuid=grpc_tensor.uuid,
    #            shape=list(grpc_tensor.shape),
    #            dtype=grpc_tensor.dtype
    #        )
