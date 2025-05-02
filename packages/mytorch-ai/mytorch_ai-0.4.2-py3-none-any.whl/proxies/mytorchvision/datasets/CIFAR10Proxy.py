###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from utils.logger import Logger
from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from gRPC_impl.mytorchvision.datasets import datasets_pb2, datasets_pb2_grpc

class CIFAR10Proxy:
    def __init__(self, root: str, train: bool, download: bool, transform_uuid: str):
        self.channel = ServerConnection.get_active_connection()
        self.root = root
        self.train = train
        self.download = download
        self.transform_uuid = transform_uuid
        self.stub = datasets_pb2_grpc.DatasetsServiceStub(self.channel)
        self.logger = Logger.get_logger()
        self.uuid = None

    @wrap_with_error_handler
    def createCIFAR10OnServer(self):
        request = datasets_pb2.CreateCIFAR10Request(root=self.root, train=self.train, download=self.download, transform_uuid=self.transform_uuid)
        response: datasets_pb2.GrpcCIFAR10 = self.stub.CreateCIFAR10onServer(request)
        self.uuid = response.uuid
        return response.uuid, response.dataset_length, response.classes