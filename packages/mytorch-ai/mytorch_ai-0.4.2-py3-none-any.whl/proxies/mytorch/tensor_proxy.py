###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

"""
This proxy provides a proxy for the Module gRPC service.
It allows the client to call specified torch.nn.Module operations on the server via gRPC.
"""

from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from gRPC_impl import shared_msg_types_pb2
from gRPC_impl.mytorch import tensor_pb2_grpc, tensor_pb2
from utils.data_transform_utils import deserialize_tensor
from utils.logger import Logger
import numpy as np
import json


from proxies.base_proxy import BaseProxy
class TensorProxy (BaseProxy):

    # Note that is is NOT used to create a tensor on the server side.
    # There are separate static methods for this.
    @wrap_with_error_handler
    def __init__(self, uuid: str):
        self.channel = ServerConnection.get_active_connection()
        self.stub = tensor_pb2_grpc.TensorServiceStub(self.channel)
        self.logger = Logger.get_logger()
        self.uuid = uuid

    @wrap_with_error_handler
    def get_data(self) -> np.ndarray:
        request = shared_msg_types_pb2.UUID(uuid=self.uuid)
        response: shared_msg_types_pb2.SerializedTensorData = self.stub.get_data(request)
        deserialized_tensor = deserialize_tensor(response.data, response.shape, response.dtype)
        return deserialized_tensor

    @wrap_with_error_handler
    def backward(self):
        request = shared_msg_types_pb2.UUID(uuid=self.uuid)
        return self.stub.backward(request)

    @wrap_with_error_handler
    def item(self) -> float:
        request = shared_msg_types_pb2.UUID(uuid=self.uuid)
        return self.stub.item(request).value

    @wrap_with_error_handler
    def float(self):
        request = shared_msg_types_pb2.UUID(uuid=self.uuid)
        grpc_tensor = self.stub.float(request)
        # can't return a mytorch.Tensor here because it would create a circular import
        return grpc_tensor.uuid, grpc_tensor.shape, grpc_tensor.dtype

    @wrap_with_error_handler
    def long(self):
        request = shared_msg_types_pb2.UUID(uuid=self.uuid)
        grpc_tensor = self.stub.long(request)
        # can't return a mytorch.Tensor here because it would create a circular import
        return grpc_tensor.uuid, grpc_tensor.shape, grpc_tensor.dtype

    @wrap_with_error_handler
    def toCuda(self):
        request = shared_msg_types_pb2.UUID(uuid=self.uuid)
        grpc_tensor = self.stub.to_cuda(request)
        return grpc_tensor.uuid, grpc_tensor.shape, grpc_tensor.dtype

    @wrap_with_error_handler
    def toCpu(self):
        request = shared_msg_types_pb2.UUID(uuid=self.uuid)
        grpc_tensor = self.stub.to_cpu(request)
        return grpc_tensor.uuid, grpc_tensor.shape, grpc_tensor.dtype

    @wrap_with_error_handler
    def reshape(self, shape: tuple):
        request = shared_msg_types_pb2.ReshapeRequest(tensor_uuid=self.uuid, shape=shape)
        grpc_tensor = self.stub.reshape(request)
        # can't return a mytorch.Tensor here because it would create a circular import
        return grpc_tensor.uuid, grpc_tensor.shape, grpc_tensor.dtype

    @wrap_with_error_handler
    def get_shape(self):
        request = shared_msg_types_pb2.UUID(uuid=self.uuid)
        grpc_tensor = self.stub.get_shape(request)
        # convert the shape from a repeated field to a tuple
        shape = tuple(grpc_tensor.shape)
        return shape

    @wrap_with_error_handler
    def get_dtype(self):
        request = shared_msg_types_pb2.UUID(uuid=self.uuid)
        grpc_tensor = self.stub.get_dtype(request)
        return grpc_tensor.dtype

    @wrap_with_error_handler
    def equal(self, other_uuid: str):
        if not isinstance(other_uuid, str):
            raise ValueError("other_uuid must be a string")
        if self.uuid == other_uuid:
            return True
        request = shared_msg_types_pb2.TwoTensorIDs(tensor1_uuid=self.uuid, tensor2_uuid=other_uuid)
        grpc_tensor = self.stub.equal(request)
        return grpc_tensor.uuid, grpc_tensor.shape, grpc_tensor.dtype

    @wrap_with_error_handler
    def add(self, other_uuid: str):
        request = shared_msg_types_pb2.TwoTensorIDs(tensor1_uuid=self.uuid, tensor2_uuid=other_uuid)
        grpc_tensor = self.stub.add(request)
        # can't return a mytorch.Tensor here because it would create a circular import
        return grpc_tensor.uuid, grpc_tensor.shape, grpc_tensor.dtype


    @wrap_with_error_handler
    def sum(self, operand):
        return self.generic_call("torch.Tensor", "sum", self.uuid, operand, call_type="method")

    @wrap_with_error_handler
    def sub(self, operand: int):
        return self.generic_call("torch.Tensor", "sub", self.uuid, operand, call_type="method")

    @wrap_with_error_handler
    def mul(self, operand: int):
        return self.generic_call("torch.Tensor", "mul", self.uuid, operand, call_type="method")

    @wrap_with_error_handler
    def pow(self, operand: int):
        return self.generic_call("torch.Tensor", "pow", self.uuid, operand, call_type="method")

    @wrap_with_error_handler
    def view(self, batch_size: int, input_size: int):
        return self.generic_call("torch.Tensor", "view", self.uuid, batch_size, input_size, call_type="method")
   
    @wrap_with_error_handler
    def t(self):
        return self.generic_call("torch.Tensor", "t", self.uuid, call_type="method")
   
    @wrap_with_error_handler
    def chunk(self, chunks: int, dim: int):
        """
        Calls a 'chunk' method on the server that splits the tensor
        into the specified number of chunks along the given dimension.
        Returns enough information to reconstruct each resulting chunk
        as a mytorch.Tensor on the client side.
        """
        response = self.generic_call("torch.Tensor", "chunk", self.uuid, chunks, dim, call_type="method")
        
        chunked_tensors = []
        for t_def in response:
            chunk_uuid = t_def[0] #"uuid"]
            chunk_shape = t_def[1] # "shape"]
            chunk_dtype = t_def[2] #"dtype"]
            chunked_tensors.append( (chunk_uuid, chunk_shape, chunk_dtype))
        
        return chunked_tensors


    @wrap_with_error_handler
    def slice(self, slicing_specs):
        slice_request = tensor_pb2.SliceRequest()
        slice_request.tensor_uuid = self.uuid

        # If slicing_specs is not a tuple, make it one for consistent handling
        if not isinstance(slicing_specs, tuple):
            slicing_specs = (slicing_specs,)
        
        # Process each dimension's slice specification
        for slice_spec in slicing_specs:
            tensor_slice = tensor_pb2.TensorSlice()
            
            # Handle integer index
            if isinstance(slice_spec, int):
                # For integer index i, it's equivalent to slice(i, i+1, 1)
                tensor_slice.start = slice_spec
                tensor_slice.stop = slice_spec + 1
                tensor_slice.step = 1
            
            # Handle slice object
            elif isinstance(slice_spec, slice):
                tensor_slice.start = slice_spec.start if slice_spec.start is not None else -1
                tensor_slice.stop = slice_spec.stop if slice_spec.stop is not None else -1
                tensor_slice.step = slice_spec.step if slice_spec.step is not None else 1
            
            else:
                raise TypeError(f"Unsupported slice specification type: {type(slice_spec)}")
            
            slice_request.slices.append(tensor_slice)

        grpc_tensor = self.stub.slice(slice_request)
        return grpc_tensor.uuid, grpc_tensor.shape, grpc_tensor.dtype

    # e.g. tensor[0]
    @wrap_with_error_handler
    def index(self, idx: int):
        request = shared_msg_types_pb2.TensorIDAndDim(tensor_uuid=self.uuid, dim=idx)
        grpc_tensor = self.stub.index(request)
        # can't return a mytorch.Tensor here because it would create a circular import
        return grpc_tensor.uuid, grpc_tensor.shape, grpc_tensor.dtype

    # Compare OLD and NEW versions of (un)squeeze: 
    @wrap_with_error_handler
    def squeeze(self, dim: int):
        return self.generic_call("torch.Tensor", "squeeze", self.uuid, dim, call_type="method")
   
    @wrap_with_error_handler
    def unsqueeze(self, dim: int):
        request = shared_msg_types_pb2.TensorIDAndDim(tensor_uuid=self.uuid, dim=dim)
        grpc_tensor = self.stub.unsqueeze(request)
        # can't return a mytorch.Tensor here because it would create a circular import
        return grpc_tensor.uuid, grpc_tensor.shape, grpc_tensor.dtype

    ### KEY METHOD: When objects go out of scope, this is called to clean up server memory.
    # See also ModuleProxy.delete
    @wrap_with_error_handler
    def delete(self):
        request = shared_msg_types_pb2.UUID(uuid=self.uuid)
        self.stub.delete(request)