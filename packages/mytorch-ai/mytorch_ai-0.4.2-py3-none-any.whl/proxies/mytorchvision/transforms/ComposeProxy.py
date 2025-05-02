###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from utils.logger import Logger
from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from gRPC_impl.mytorchvision.transforms import transforms_pb2, transforms_pb2_grpc

class ComposeProxy:
    def __init__(self, transform_uuids: list):
        self.channel = ServerConnection.get_active_connection()
        self.stub = transforms_pb2_grpc.TransformsServiceStub(self.channel)
        self.logger = Logger.get_logger()
        self.transform_uuids = transform_uuids

    @wrap_with_error_handler
    def createTransformOnServer(self):
        request = transforms_pb2.CreateComposeTransformRequest()
        request.component_transform_uuid.extend(self.transform_uuids)
        response: transforms_pb2.GrpcTransform = self.stub.CreateComposeTransform(request)
        return response.uuid
