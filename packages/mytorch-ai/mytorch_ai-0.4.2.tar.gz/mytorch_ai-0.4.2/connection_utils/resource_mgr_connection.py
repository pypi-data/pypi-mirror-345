###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

"""
This singleton class gets the gRPC connection to the server.
"""
import grpc
import time

from utils.logger import Logger
from utils.MyTorchClient import MyTorchClient
from proxies.mytorch.scaffolding.resource_mgmt_proxy import ResourceMgmtProxy

class ResourceMgrConnection:

    def __init__(self, ip, port=50051):
        self.logger = Logger.get_logger()
        self.grpc_channel = None
        self.resource_mgr_ip = ip
        self.resource_mgr_port = port
        self.grpc_channel = None
        self.client_ip = None

        # Create a channel with the Resource Manager
        initial_channel = grpc.insecure_channel(self.resource_mgr_ip + ":" + str(self.resource_mgr_port))
        logging_interceptor = LoggingInterceptor()

        # Add the interceptors to the channel
        self.grpc_channel = grpc.intercept_channel(initial_channel, logging_interceptor)
        self.logger.info(f"Connected to Resource Manager {self.resource_mgr_ip}:{self.resource_mgr_port}")

    def get_destination_server_for_client(self, client_ip) -> dict:
        self.client_ip = client_ip
        auth_token = "FFFFFFFFFFFF"
        max_time = "1000"
        resource_mgr_proxy = ResourceMgmtProxy(self.grpc_channel)
        resource_info_dict = resource_mgr_proxy.resource_request(auth_token=auth_token, client_ip=self.client_ip, server_id=self.resource_mgr_ip, max_time=int(max_time))
        while resource_info_dict['resource_id'] == "":
            resource_info_dict = resource_mgr_proxy.resource_request(auth_token=auth_token, client_ip=self.client_ip, server_id=self.resource_mgr_ip, max_time=int(max_time))
            print(f"Waiting...   ", resource_info_dict['resource_id'])
            if resource_info_dict['resource_id'] == "":
                time.sleep(5)
        return resource_info_dict


###########################################################################
#### Interceptor to add client-side logging of gRPC calls
###########################################################################
class LoggingInterceptor(grpc.UnaryUnaryClientInterceptor,
                         grpc.UnaryStreamClientInterceptor,
                         grpc.StreamUnaryClientInterceptor,
                         grpc.StreamStreamClientInterceptor):
    def __init__(self):
        self.logger = Logger.get_logger()

    def intercept_unary_unary(self, continuation, client_call_details, request):
        return self._intercept_call(continuation, client_call_details, request)

    def intercept_unary_stream(self, continuation, client_call_details, request):
        return self._intercept_call(continuation, client_call_details, request)

    def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
        return self._intercept_stream_call(continuation, client_call_details, request_iterator)

    def intercept_stream_stream(self, continuation, client_call_details, request_iterator):
        return self._intercept_stream_call(continuation, client_call_details, request_iterator)

    def _intercept_call(self, continuation, client_call_details, request):
        method_name = client_call_details.method
        self.logger.debug(f"~~~~~~~~~ Outgoing request ~~~~~~~~~")
        self.logger.debug(f"Calling gRPC method: {method_name}")

        start_time = time.perf_counter()
        response = continuation(client_call_details, request)
        self._log_duration(method_name, start_time)
        self._log_response(method_name, response)
        return response

    def _intercept_stream_call(self, continuation, client_call_details, request_iterator):
        method_name = client_call_details.method
        self.logger.debug(f"~~~~~~~~~ Outgoing stream request ~~~~~~~~~")
        self.logger.debug(f"Calling gRPC streaming method: {method_name}")

        start_time = time.perf_counter()

        # Wrap the request iterator to add logging
        wrapped_iterator = self._log_stream_requests(request_iterator)

        response = continuation(client_call_details, wrapped_iterator)
        self._log_duration(method_name, start_time)
        self._log_response(method_name, response)
        return response

    def _log_duration(self, method_name, start_time):
        end_time = time.perf_counter()
        duration = end_time - start_time
        rounded_duration = round(1000 * duration, 2)  # Convert to milliseconds and round to 2 decimal places
        self.logger.debug(f"Method {method_name} took: {rounded_duration} ms")
        MyTorchClient.instance().add_method_duration(method_name, duration)
        return duration

    def _log_response(self, method_name, response):
        self.logger.debug("~~~~~~~~~ Incoming response ~~~~~~~~~")
        self.logger.debug(f"Received gRPC method: {method_name}")
        self.logger.debug("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        return response

    def _log_stream_requests(self, request_iterator):
        for request in request_iterator:
            self.logger.debug(f"Streaming request: {request}")
            yield request

