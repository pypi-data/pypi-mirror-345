###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

"""
This proxy provides a proxy for the Module gRPC service.
It allows the client to call specified torch.nn.Module operations on the server via gRPC.
"""

from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from gRPC_impl.mytorch.nn import module_pb2_grpc, nn_msg_types_pb2, module_pb2
from gRPC_impl import shared_msg_types_pb2
from utils.data_transform_utils import deserialize_state_dict
from utils.logger import Logger
from torch.Tensor import Tensor
from torch.nn.ParametersGenerator import ParametersGenerator
from proxies.mytorch.scaffolding.scaffolding_proxy import ScaffoldingProxy
from proxies.base_proxy import BaseProxy

import numpy as np

class ModuleProxy( BaseProxy ):
    # if uuid is None, it means that the module is not yet created and
    # one will be created when initializing the proxy
    def __init__(self):
        self.channel = ServerConnection.get_active_connection()
        self.module_stub = module_pb2_grpc.ModuleServiceStub(self.channel)
        self.logger = Logger.get_logger()
        self.uuid = None

    @wrap_with_error_handler
    def create_module_on_server(self):
        # Notify the server to create a real torch.nn.Module
        return_val = self.module_stub.CreateModuleOnServer(shared_msg_types_pb2.Empty())
        self.uuid = return_val.uuid
        self.logger.info("ModuleProxy: Created proxy with ID: " + return_val.uuid)
        return return_val.uuid

    @wrap_with_error_handler
    def state_dict(self):
        self.logger.debug(f"Getting state_dict for proxy with ID `{self.uuid}`")
        # Request the state_dict from the server
        request = shared_msg_types_pb2.UUID(uuid=self.uuid)
        stream = self.module_stub.GetStateDict(request)

        state_dict = {}
        for named_tensor in stream:
            tensor_proxy = Tensor(
                uuid=named_tensor.tensor.uuid,
                shape=list(named_tensor.tensor.shape),
                dtype=named_tensor.tensor.dtype,
            )
            state_dict[named_tensor.name] = tensor_proxy

        return state_dict

    @wrap_with_error_handler
    def load_state_dict(self, state_dict: dict) -> None:
        self.logger.debug(f"Uploading state_dict to module `{self.uuid}`")

        def chunk_generator():
            for name, tensor in state_dict.items():
                if not isinstance(tensor, Tensor):
                    raise TypeError(f"Expected Tensor proxy for key '{name}', got {type(tensor)}")

                grpc_tensor = shared_msg_types_pb2.GrpcTensor(
                    uuid=tensor.uuid,
                    shape=tensor.shape,
                    dtype=tensor.dtype,
                )

                yield shared_msg_types_pb2.NamedTensor(
                    name=name,
                    tensor=grpc_tensor
                )

        # Server will use self.uuid to apply state_dict
        
        metadata = (("module-uuid", self.uuid),)
        response = self.module_stub.LoadStateDict(chunk_generator(), metadata=metadata)

        if not response.value:
            raise RuntimeError("Failed to load state_dict on the server.")


    @wrap_with_error_handler
    def forward(self, input_data) -> Tensor:
        # for some reason, right now the train_test_split function
        # is returning a list of numpy arrays, so convert it here
        # TODO: fix this in the train_test_split function
        if isinstance(input_data, np.ndarray):
            tensor_uuid = MyTorchProxy().from_numpy(input_data).uuid

        # if the input_data is a PyTorch tensor, send it to the server
        # and get the UUID of the tensor on the server
        # elif isinstance(input_data, torch.Tensor):
        #     tensor_uuid = MyTorchProxy().send_pytorch_tensor_to_server(input_data).uuid

        # this is a MyTorch tensor
        else:
            tensor_uuid = input_data.uuid

        request = nn_msg_types_pb2.ForwardPassRequest()
        request.module_uuid = self.uuid
        request.tensor_uuid = tensor_uuid
        response: shared_msg_types_pb2.GrpcTensor = self.module_stub.Forward(request)
        return Tensor(response.uuid, response.shape, response.dtype)

    @wrap_with_error_handler
    def eval(self):
        request = shared_msg_types_pb2.UUID(uuid=self.uuid)
        self.module_stub.Eval(request)

    @wrap_with_error_handler
    def to_device(self, device: str) -> None:
        request = module_pb2.ModuleToDeviceRequest(uuid=self.uuid, device=device)
        response = self.module_stub.ToDevice(request)

    @wrap_with_error_handler
    def parameters(self):
        """
        Uses generic_call instead of gRPC GetParameters.
        Calls model.parameters() using call_type="method".
        Returns a list of Tensor proxy objects.
        """
        results = self.generic_call("torch.nn", "parameters", self.uuid, call_type="method")

        # The response should be a list of (uuid, shape, dtype) tuples
        if not isinstance(results, list):
            raise RuntimeError("Expected list of parameters from generic_call")

        tensors = []
        for entry in results:
            if not isinstance(entry, tuple) or len(entry) != 3:
                raise ValueError(f"Invalid tensor response format: {entry}")
            uuid, shape, dtype = entry
            tensors.append(Tensor(uuid=uuid, shape=shape, dtype=dtype))

        return tensors

    @wrap_with_error_handler
    def half(self):
        request = module_pb2.half_request(uuid=self.uuid)
        self.module_stub.half(request)

    ### KEY METHOD: When objects go out of scope, this is called to clean up server memory.
    # See also TensorProxy.delete
    @wrap_with_error_handler
    def delete(self):
        request = shared_msg_types_pb2.UUID(uuid=self.uuid)
        self.module_stub.delete(request)

    @wrap_with_error_handler
    def train(self, mode=True):
        # Torch uses .train(True) or .train(False)
        return self.generic_call("torch.nn", "train", self.uuid, mode, call_type="method")
