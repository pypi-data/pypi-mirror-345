###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from utils.logger import Logger
from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from gRPC_impl.mytorchvision.transforms import transforms_pb2, transforms_pb2_grpc

class NormalizeProxy:
    def __init__(self, mean: list, std: list):
        self.channel = ServerConnection.get_active_connection()
        self.stub = transforms_pb2_grpc.TransformsServiceStub(self.channel)
        self.logger = Logger.get_logger()
        self.mean = mean
        self.std = std

    @wrap_with_error_handler
    def createTransformOnServer(self):
        request = transforms_pb2.CreateNormalizeTransformRequest()
        request.mean.extend(self.mean)
        request.std.extend(self.std)
        response: transforms_pb2.GrpcTransform = self.stub.CreateNormalizeTransform(request)
        return response.uuid