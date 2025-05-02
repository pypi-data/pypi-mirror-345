###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from utils.logger import Logger
from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from gRPC_impl.mytorchvision.datasets import datasets_pb2, datasets_pb2_grpc
from gRPC_impl.mytorch.scaffolding import data_mgmt_pb2_grpc


class ImageFolderProxy:
    def __init__(self):
        self.channel = ServerConnection.get_active_connection()
        self.relative_datapath = None
        self.transform_uuid = None
        self.datasets_stub = datasets_pb2_grpc.DatasetsServiceStub(self.channel)
        self.data_mgmt_stub = data_mgmt_pb2_grpc.DataMgmtServiceStub(self.channel)
        self.logger = Logger.get_logger()

    @wrap_with_error_handler
    def createImageFolderOnServer(self, relative_datapath: str, transform_uuid: str):
        self.relative_datapath = relative_datapath
        self.transform_uuid = transform_uuid
        request = datasets_pb2.CreateImageFolderRequest(relative_datapath=self.relative_datapath, transform_uuid=self.transform_uuid)
        response: datasets_pb2.GrpcImageFolder = self.datasets_stub.CreateImageFolderOnServer(request)
        return response.uuid, response.image_uuids, response.labels, response.classes