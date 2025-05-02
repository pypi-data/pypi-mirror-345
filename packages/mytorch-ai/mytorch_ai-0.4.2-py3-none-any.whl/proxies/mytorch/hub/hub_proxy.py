###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from gRPC_impl.mytorch.hub import hub_pb2, hub_pb2_grpc
from torchvision.models import WeightsEnum
from utils.logger import Logger

class HubProxy:
    def __init__(self):
        self.channel = ServerConnection.get_active_connection()
        self.stub = hub_pb2_grpc.HubServiceStub(self.channel)
        self.logger = Logger.get_logger()
        self.uuid = None

    # example call: torch.hub.load('pytorch/vision:v0.6.0', 'resnet18', weights=ResNet18_Weights.DEFAULT)
    @wrap_with_error_handler
    def load_module_from_repo(self, repo: str, model_name: str, weights: WeightsEnum) -> str:
        # Load a model from the PyTorch Hub
        request = hub_pb2.ModelLoadRequest(repo=repo, model_name=model_name, weights_enum=weights.name)
        response = self.stub.loadModel(request)
        self.logger.info(f"Loaded model from repo {repo} with model name {model_name}")
        return response.model_uuid