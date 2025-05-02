###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

"""
This proxy provides a proxy for the MyTorchService gRPC service.
It allows the client to call specified torch operations on the server via gRPC.
"""

from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from gRPC_impl.mytorch.cuda import cuda_pb2_grpc, cuda_pb2
from gRPC_impl.shared_msg_types_pb2 import Empty
from utils.logger import Logger
from proxies.base_proxy import BaseProxy


class CudaProxy (BaseProxy):

    def __init__(self):
        self.channel = ServerConnection.get_active_connection()
        self.stub = cuda_pb2_grpc.CudaServiceStub(self.channel)
        self.logger = Logger.get_logger()

    #@wrap_with_error_handler
    #def is_available(self) -> bool:
    #    response: cuda_pb2.is_available_response = self.stub.is_available(cuda_pb2.is_available_request())
    #    return response.is_available
    
    @wrap_with_error_handler
    def is_available(self) -> bool:
        is_avail = self.generic_call("torch.cuda", "is_available")
        return is_avail

    #@wrap_with_error_handler
    #def get_device_name(self) -> str:
    #    response: cuda_pb2.get_device_name_response = self.stub.get_device_name(Empty())
    #    return response.value

    @wrap_with_error_handler
    def get_device_name(self) -> str:
        response= self.generic_call("torch.cuda", "get_device_name")
        return response

    @wrap_with_error_handler
    def empty_cache(self):
        self.stub.empty_cache(cuda_pb2.empty_cache_request())

    @wrap_with_error_handler
    def memory_allocated(self) -> int:
        response: cuda_pb2.memory_allocated_response = self.stub.memory_allocated(cuda_pb2.memory_allocated_request())
        return response.memory_allocated

    @wrap_with_error_handler
    def memory_reserved(self) -> int:
        response: cuda_pb2.memory_reserved_response = self.stub.memory_reserved(cuda_pb2.memory_reserved_request())
        return response.memory_reserved

    @wrap_with_error_handler
    def get_device_properties(self, device) -> dict:
        if isinstance(device, str):
            request = cuda_pb2.get_device_properties_request(device_str=device)
        elif isinstance(device, int):
            request = cuda_pb2.get_device_properties_request(device_int=device)
        else:
            self.logger.error("No device specified")
            return {}
        response: cuda_pb2.get_device_properties_response = self.stub.get_device_properties(request)
        return {
            "name": response.name,
            "total_memory": response.total_memory,
            "available_memory": response.available_memory,
            "allocated_memory": response.allocated_memory,
            "reserved_memory": response.reserved_memory,
            "max_memory_allocated": response.max_memory_allocated,
            "max_memory_reserved": response.max_memory_reserved,
            "multi_processor_count": response.multi_processor_count
        }
