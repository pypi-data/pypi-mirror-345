###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from utils.logger import Logger
from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from gRPC_impl.mytorchvision.transforms import transforms_pb2, transforms_pb2_grpc
from gRPC_impl import shared_msg_types_pb2

class ToTensorProxy:
    def __init__(self):
        self.channel = ServerConnection.get_active_connection()
        self.stub = transforms_pb2_grpc.TransformsServiceStub(self.channel)
        self.logger = Logger.get_logger()

    @wrap_with_error_handler
    def createTransformOnServer(self):
        request = shared_msg_types_pb2.Empty()
        response: transforms_pb2.GrpcTransform = self.stub.CreateToTensorTransform(request)
        return response.uuid