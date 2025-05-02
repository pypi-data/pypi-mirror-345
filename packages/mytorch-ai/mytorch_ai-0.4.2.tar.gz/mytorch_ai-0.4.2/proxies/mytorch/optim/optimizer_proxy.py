###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from gRPC_impl.mytorch.optim import optimizers_pb2_grpc, optimizers_pb2
from gRPC_impl import shared_msg_types_pb2
from utils.logger import Logger

from proxies.base_proxy import BaseProxy

class OptimizerProxy(BaseProxy):
    def __init__(self):
        super().__init__()

        self.channel = ServerConnection.get_active_connection()
        self.stub = optimizers_pb2_grpc.OptimizerServiceStub(self.channel)
        self.logger = Logger.get_logger()
        self.uuid = None

    @wrap_with_error_handler
    def create_SGD(self, generator_uuid: str, learning_rate: float, momentum):
        request = optimizers_pb2.CreateSGDOptimizerRequest()
        request.generator_uuid = generator_uuid
        request.learning_rate = learning_rate
        request.momentum = momentum
        response = self.stub.CreateSGDOptimizer(request)
        return response.uuid

    @wrap_with_error_handler
    def zero_grad(self):
        uuid_msg = shared_msg_types_pb2.UUID(uuid=self.uuid)
        return self.stub.ZeroGrad(uuid_msg)

    @wrap_with_error_handler
    def step(self):
        uuid_msg = shared_msg_types_pb2.UUID(uuid=self.uuid)
        return self.stub.Step(uuid_msg)
