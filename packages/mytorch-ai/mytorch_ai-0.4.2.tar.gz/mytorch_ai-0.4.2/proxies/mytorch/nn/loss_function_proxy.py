###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from gRPC_impl.mytorch.nn import loss_functions_pb2_grpc, loss_functions_pb2
from proxies.mytorch.scaffolding.scaffolding_proxy import ScaffoldingProxy
from torch.Tensor import Tensor
from utils.logger import Logger
import numpy as np

class LossFunctionProxy:
    def __init__(self, loss_function_type: loss_functions_pb2.LossFunctionType):
        self.channel = ServerConnection.get_active_connection()
        self.stub = loss_functions_pb2_grpc.LossFunctionServiceStub(self.channel)
        self.logger = Logger.get_logger()
        # Create a LossFunctionRequest object
        request = loss_functions_pb2.LossFunctionRequest()
        request.loss_function_type = loss_function_type
        self.loss_function_uuid = self.stub.CreateLossFunction(request).uuid
        self.loss_function_type = loss_function_type

    @classmethod
    def create_CrossEntropyLoss(cls):
        return cls(loss_functions_pb2.CrossEntropy)

    @wrap_with_error_handler
    def run_loss(self, input_data, target) -> Tensor:
        # for some reason, right now the train_test_split function
        # is returning a list of numpy arrays, so convert it here
        # TODO: fix this in the train_test_split function
        if isinstance(input_data, np.ndarray):
            input_uuid = MyTorchProxy().from_numpy(input_data).uuid
        else:
            input_uuid = input_data.uuid

        if isinstance(target, np.ndarray):
            target_uuid = MyTorchProxy().from_numpy(target).uuid
        else:
            target_uuid = target.uuid

        request = loss_functions_pb2.RunLossFunctionRequest()
        request.loss_function_uuid = self.loss_function_uuid
        request.input_uuid = input_uuid
        request.target_uuid = target_uuid

        response = self.stub.RunLossFunction(request)
        return Tensor(response.uuid, response.shape, response.dtype)

