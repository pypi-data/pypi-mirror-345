###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

"""
This proxy provides a proxy for the MyTorchService gRPC service.
It allows the client to call specified torch operations on the server via gRPC.
"""

from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from gRPC_impl.mytorch import mytorch_pb2_grpc, mytorch_pb2
from gRPC_impl import shared_msg_types_pb2
from torch.Tensor import Tensor
from torch.device import device
from utils.logger import Logger
from utils import data_transform_utils
import json
import os

from proxies.base_proxy import BaseProxy
CHUNK_SIZE = 1 * 1024 * 1024  # 1MB default

class MyTorchProxy (BaseProxy):

    def __init__(self):
        self.channel = ServerConnection.get_active_connection()
        self.stub = mytorch_pb2_grpc.MyTorchServiceStub(self.channel)
        self.logger = Logger.get_logger()

    @wrap_with_error_handler
    def rand(self, *size: int):
        uuid, shape, dtype = self.generic_call("torch", "rand", *size)
        return Tensor(uuid, shape, dtype)
    
    @wrap_with_error_handler
    def randn(self, *sizes) -> Tensor:
    # Convert sizes to tuple if it's a list
        if len(sizes) == 1 and isinstance(sizes[0], list):
            sizes_tuple = tuple(sizes[0])
        else:
            sizes_tuple = sizes
            
        uuid, shape, dtype = self.generic_call("torch", "randn", sizes_tuple)
        return Tensor(uuid, shape, dtype)

    @wrap_with_error_handler
    def zeros(self, *size: int):
        uuid, shape, dtype = self.generic_call("torch", "zeros", *size)
        return Tensor(uuid, shape, dtype)
    
    @wrap_with_error_handler
    def ones(self, *size: int):
        uuid, shape, dtype = self.generic_call("torch", "ones", *size)
        return Tensor(uuid, shape, dtype)
    
    @wrap_with_error_handler
    def from_numpy(self, np_array) -> Tensor:
        request = data_transform_utils.serialize_numpy_array(np_array)
        response: shared_msg_types_pb2.GrpcTensor = self.stub.from_numpy(request)
        tensor = Tensor(response.uuid, response.shape, response.dtype)
        tensor._retrieved_data = np_array # since we already have the data, we don't need to fetch it again
        return tensor

    @wrap_with_error_handler
    def max(self, tensor: Tensor, dim: int) -> tuple[Tensor, Tensor]:
        request = shared_msg_types_pb2.TensorIDAndDim(tensor_uuid=tensor.uuid, dim=dim)
        response: shared_msg_types_pb2.TwoGrpcTensors = self.stub.max(request)
        max_value = Tensor(response.tensor1.uuid, response.tensor1.shape, response.tensor1.dtype)
        max_indices = Tensor(response.tensor2.uuid, response.tensor2.shape, response.tensor2.dtype)
        return max_value, max_indices

    @wrap_with_error_handler
    def arange(self, start, end, step) -> Tensor:
        request = mytorch_pb2.ARangeRequest(start=start, end=end, step=step)
        response_tensor: shared_msg_types_pb2.GrpcTensor = self.stub.arange(request)
        return Tensor(response_tensor.uuid, response_tensor.shape, response_tensor.dtype)

    @wrap_with_error_handler
    def meshgrid(self, tensor_uuids, indexing) -> tuple:
        request = shared_msg_types_pb2.TensorIDsAndDim()
        request.tensor_uuids.extend(tensor_uuids)
        request.dim = indexing
        response: shared_msg_types_pb2.MultipleGrpcTensors = self.stub.meshgrid(request)
        tensors = [Tensor(tensor.uuid, tensor.shape, tensor.dtype) for tensor in response.tensors]
        return tuple(tensors)

    @wrap_with_error_handler
    def reshape(self, tensor: Tensor, shape: tuple) -> Tensor:
        request = shared_msg_types_pb2.ReshapeRequest(tensor_uuid=tensor.uuid, shape=shape)
        response: shared_msg_types_pb2.GrpcTensor = self.stub.reshape(request)
        return Tensor(response.uuid, response.shape, response.dtype)

    @wrap_with_error_handler
    def cat(self, tensors: list, dim: int) -> Tensor:
        request = shared_msg_types_pb2.TensorIDsAndDim()
        request.tensor_uuids.extend([tensor.uuid for tensor in tensors])
        request.dim = dim
        response: shared_msg_types_pb2.GrpcTensor = self.stub.cat(request)
        return Tensor(response.uuid, response.shape, response.dtype)

    @wrap_with_error_handler
    def argmax(self, tensor: Tensor, dim: int, keepdim: bool) -> Tensor:
        request = mytorch_pb2.ArgMaxRequest(tensor_uuid=tensor.uuid, dim=dim, keepdim=keepdim)
        response: shared_msg_types_pb2.GrpcTensor = self.stub.argmax(request)
        return Tensor(response.uuid, response.shape, response.dtype)

    @wrap_with_error_handler
    def matmul(self, tensor1: Tensor, tensor2: Tensor) -> Tensor:
        uuid, shape, dtype = self.generic_call("torch", "matmul", tensor1.uuid, tensor2.uuid)
        return Tensor(uuid, shape, dtype)
    
    @wrap_with_error_handler
    def device(self, dev: str) -> device:
        returned_dev = self.generic_call("torch", "device", dev)
        return device(returned_dev)


    @wrap_with_error_handler
    def save(self, state_dict: dict, file_path: str):
        named_tensor_uuids = {
            k: v.uuid for k, v in state_dict.items() if isinstance(v, Tensor)
        }
        request = mytorch_pb2.SaveModelRequest(
            filename=os.path.basename(file_path),
            named_tensor_uuids=named_tensor_uuids
        )
        chunk_stream = self.stub.save_model_stream(request)

        with open(file_path, "wb") as f:
            for chunk in chunk_stream:
                f.write(chunk.chunk_data)

    @wrap_with_error_handler
    def load(self, file_path: str):
        filename = os.path.basename(file_path)
        def chunk_generator():
            with open(file_path, "rb") as f:
                index = 0
                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    yield shared_msg_types_pb2.FileChunk(
                        filename=filename,
                        chunk_data=chunk,
                        chunk_index=index,
                        is_last_chunk=False
                    )
                    index += 1
                yield shared_msg_types_pb2.FileChunk(
                    filename=filename,
                    chunk_data=b"",
                    chunk_index=index,
                    is_last_chunk=True
                )

        response = self.stub.load_model_stream(chunk_generator())
        return {
            name: Tensor(t.uuid, list(t.shape), t.dtype)
            for name, t in response.tensors.items()
        }

    @wrap_with_error_handler
    def allclose(self, input: Tensor, other: Tensor, rtol: float = 1e-05, atol: float = 1e-08, equal_nan: bool = False) -> bool:
        request = mytorch_pb2.AllCloseRequest(tensor1_uuid=input.uuid, tensor2_uuid=other.uuid, rtol=rtol, atol=atol, equal_nan=equal_nan)
        response = self.stub.allclose(request)
        return response.value

    @wrap_with_error_handler
    def unsqueeze(self, tensor: Tensor, dim: int) -> Tensor:
        request = shared_msg_types_pb2.TensorIDAndDim(tensor_uuid=tensor.uuid, dim=dim)
        response: shared_msg_types_pb2.GrpcTensor = self.stub.unsqueeze(request)
        return Tensor(response.uuid, response.shape, response.dtype)

    def repeat_interleave(self, tensor: Tensor, repeats: int, dim: int) -> Tensor:
        request = mytorch_pb2.RepeatInterleaveRequest(tensor_uuid=tensor.uuid, repeats=repeats, dim=dim)
        response: shared_msg_types_pb2.GrpcTensor = self.stub.repeat_interleave(request)
        return Tensor(response.uuid, response.shape, response.dtype)

    @wrap_with_error_handler
    def tanh(self, tensor: Tensor) -> Tensor:
        uuid, shape, dtype = self.generic_call("torch", "tanh", tensor.uuid)
        return Tensor(uuid, shape, dtype)


    @wrap_with_error_handler
    def sigmoid(self, tensor: Tensor) -> Tensor:
        uuid, shape, dtype = self.generic_call("torch", "sigmoid", tensor.uuid)
        return Tensor(uuid, shape, dtype)


    @wrap_with_error_handler    
    def stack(self, tensor_uuids, dim: int = 0):
        uuid, shape, dtype  = self.generic_call("torch", "stack", tensor_uuids, dim)
        return Tensor(uuid, shape, dtype)

    @wrap_with_error_handler
    def mean(self, tensor: Tensor, dim=None, keepdim=False, in_dtype=None, out=None) -> Tensor:
        if dim is None and keepdim is False and in_dtype is None and out is None:
            uuid, shape, dtype = self.generic_call("torch", "mean", tensor.uuid)
        elif dim is not None and keepdim is False and in_dtype is None and out is None:
            uuid, shape, dtype = self.generic_call("torch", "mean", tensor.uuid, dim)
        else:
            uuid, shape, dtype = self.generic_call("torch", "mean", tensor.uuid, dim, keepdim, in_dtype, out)
        return Tensor(uuid, shape, dtype)


    @wrap_with_error_handler
    def equal(self, tensor1: Tensor, tensor2: Tensor) -> bool:
        yesno = self.generic_call("torch", "equal", tensor1.uuid, tensor2.uuid)
        return yesno
    
    ### CACHEQ methods:

    @wrap_with_error_handler
    def scaffolding_server_get_timing_statistics(self, run_id: str) -> str:
        request = shared_msg_types_pb2.StringValue()
        request.value = run_id
        return self.stub.scaffolding_server_get_timing_statistics(request) 
    
    @wrap_with_error_handler
    def scaffolding_server_initialize_timing_statistics(self, run_id: str):
        request = shared_msg_types_pb2.StringValue()
        request.value = run_id
        self.stub.scaffolding_server_initialize_timing_statistics(request)
