###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from gRPC_impl.mytorch.jit import jit_pb2, jit_pb2_grpc
from gRPC_impl import shared_msg_types_pb2
from torch.nn.Module import Module
from torch.Tensor import Tensor
from utils.logger import Logger

class JitProxy:
    def __init__(self):
        self.channel = ServerConnection.get_active_connection()
        self.stub = jit_pb2_grpc.JitServiceStub(self.channel)
        self.logger = Logger.get_logger()
        self.uuid = None

    @wrap_with_error_handler
    def trace(self, model: Module, example_input: Tensor) -> str:
        # Load a model from the PyTorch Hub
        request = jit_pb2.ModelIDandTensorID(model_uuid=model.uuid, tensor_uuid=example_input.uuid)
        response = self.stub.trace(request)
        self.logger.info(f"Traced model has been generated")
        return response.uuid

    @wrap_with_error_handler
    def save(self, module: Module, path: str) -> None:
        request = jit_pb2.SaveRequest(model_uuid=module.uuid, path=path)
        self.stub.save(request)
        self.logger.info(f"Model has been saved to {path}")

    @wrap_with_error_handler
    def load(self, path: str) -> str:
        request = shared_msg_types_pb2.StringValue(value=path)
        response = self.stub.load(request)
        self.logger.info(f"Model has been loaded from {path}")
        return response.uuid