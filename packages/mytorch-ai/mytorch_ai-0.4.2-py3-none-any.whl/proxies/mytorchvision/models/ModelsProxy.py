###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from utils.logger import Logger
from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from torchvision.models.weight_enums import WeightsEnum
from gRPC_impl.mytorchvision.models import models_pb2, models_pb2_grpc

class ModelsProxy:
    def __init__(self):
        self.channel = ServerConnection.get_active_connection()
        self.logger = Logger.get_logger()
        self.stub = models_pb2_grpc.ModelsServiceStub(self.channel)

    @wrap_with_error_handler
    def resnet18(self, weights: WeightsEnum):
        request = models_pb2.WeightEnumString(value=weights.name)
        response = self.stub.resnet18(request)
        return response.uuid

    @wrap_with_error_handler
    def resnet50(self, weights: WeightsEnum):
        request = models_pb2.WeightEnumString(value=weights.name)
        response = self.stub.resnet50(request)
        return response.uuid

    @wrap_with_error_handler
    def resnet152(self, weights: WeightsEnum):
        request = models_pb2.WeightEnumString(value=weights.name)
        response = self.stub.resnet152(request)
        return response.uuid