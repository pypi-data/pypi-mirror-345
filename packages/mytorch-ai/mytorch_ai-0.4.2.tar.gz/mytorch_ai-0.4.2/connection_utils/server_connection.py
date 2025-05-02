###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

"""
This singleton class gets the gRPC connection to the server.
"""
import grpc
from utils.logger import Logger
import time
from utils.MyTorchClient import MyTorchClient
import signal
import os
import sys
import atexit
import threading

###########################################################################
#### ServerConnection; only has one connection to the server
#### All methods are class methods.
#### _connection_is_active is thread safe; if True, all subsequent calls are ignored
###########################################################################

class ServerConnection:
    _lock = threading.Lock() # lock to ensure that only one thread can access the connection at a time
    _channel = None
    _server = None
    _port = 50051 # default
    _connection_is_active = False # set to True when disconnect is called so all subsequent calls are ignored

    @classmethod
    def get_server_ip(cls):
        return cls._server, cls._port

    @classmethod
    def close_connection(cls):
        with cls._lock:
            cls._connection_is_active = True

    @classmethod
    def open_connection(cls):
        with cls._lock:
            cls._connection_is_active = False

    @classmethod
    def is_connection_active(cls):
        with cls._lock:
            return cls._connection_is_active

    @classmethod
    def check_mytorch_token(cls):
        """
        Check for MyTorch token in environment variables or config file.
        Raises RuntimeError if token is not found.
        """
        # First check environment variable
        token = os.getenv('MYTORCH_TOKEN')
        if token:
            return token

        # Check ~/.mytorch file
        config_path = os.path.expanduser('~/.mytorch')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                for line in f:
                    if 'token' in line and '=' in line:
                        # Split on '=' and strip whitespace from both parts
                        parts = line.split('=', 1)
                        if parts[0].strip() == 'token':
                            token = parts[1].strip()
                            # Set the environment variable for future use
                            os.environ['MYTORCH_TOKEN'] = token
                            return token

        print("*** ERROR -- MyTorch token not found.\n"
              "*** Please add 'token=<your_token>' to ~/.mytorch file or set the MYTORCH_TOKEN environment variable", file=sys.stderr)
        sys.exit(1)

    @classmethod
    def get_active_connection(cls):
        """
        If there is no connection, connect to the server and register client
        If connection is active, return the existing connection
        """
        if cls._channel is None:
            # Check for token before attempting connection
            cls.check_mytorch_token()

            # if the server is specified in the environment variable, use that, otherwise use the proxy
            if os.getenv('MYTORCH_SERVER_IP') is not None:
                cls._server, cls._port = MyTorchClient.instance().select_server_by_env_var()
            else:
                response = MyTorchClient.instance().select_server_by_proxy()
                if response is not None:
                    cls._server, cls._port = response
                else:
                    Logger.get_logger().error("Invalid access token or failed to connect to mytorch server")
                    sys.exit(1)

            # Create a channel with the server
            channel = grpc.insecure_channel(cls._server + ":" + str(cls._port))
            # Define the metadata to be added
            client_id = MyTorchClient.instance().get_client_id()
            metadata = [('client_id', client_id)]

            register_cleanup_handlers()

            """
            ... currently don't need this, but this is how you would add more metadata
            to the connection.
            
            client_info = MyTorchClient.instance().get_client_info()
            metadata.extend([
                ('hostname', client_info['hostname']),
                ('local_ip', client_info['local_ip']),
                ('os_name', client_info['os_name']),
                ('os_version', client_info['os_version']),
                ('os_release', client_info['os_release']),
                ('os_details', client_info['os_details']),
                ('mytorch_version', client_info['mytorch_version']),
                ('machine', client_info['machine']),
                ('processor', client_info['processor']),
                ('token', client_info['token']),
            """

            metadata_interceptor = MetadataInterceptor(metadata)
            logging_interceptor = LoggingInterceptor()

            # Add the interceptors to the channel
            try:
                cls._channel = grpc.intercept_channel(channel, logging_interceptor, metadata_interceptor)
                cls.open_connection()
                Logger.get_logger().info(f"Connecting to server {cls._server}:{cls._port}")
            except Exception as e:
                Logger.get_logger().error(f"Error connecting to server {cls._server}:{cls._port}")
                Logger.get_logger().error(f"Error details: {e}")
                sys.exit(1)

            # if we get here, we are connected to the server; now we need to register the client
            client_info = MyTorchClient.instance().get_client_info()
            from proxies.mytorch.scaffolding.scaffolding_proxy import ScaffoldingProxy
            response = ScaffoldingProxy().register_client_with_server(client_info)
            if response is not None and str(response) != "":
                Logger.get_logger().error(f"Error registering client with server: {response}")
                sys.exit(1)
        return cls._channel

###########################################################################
#### Interceptor to add metadata (e.g. Client UUID) to each outgoing request
###########################################################################
class MetadataInterceptor(
    grpc.UnaryUnaryClientInterceptor,
    grpc.UnaryStreamClientInterceptor,
    grpc.StreamUnaryClientInterceptor,
    grpc.StreamStreamClientInterceptor
):
    def __init__(self, metadata):
        self._metadata = metadata

    def intercept_unary_unary(self, continuation, client_call_details, request):
        new_details = self._augment_metadata(client_call_details)
        return continuation(new_details, request)

    def intercept_unary_stream(self, continuation, client_call_details, request):
        new_details = self._augment_metadata(client_call_details)
        return continuation(new_details, request)

    def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
        new_details = self._augment_metadata(client_call_details)
        return continuation(new_details, request_iterator)

    def intercept_stream_stream(self, continuation, client_call_details, request_iterator):
        new_details = self._augment_metadata(client_call_details)
        return continuation(new_details, request_iterator)

    def _augment_metadata(self, client_call_details):
        new_metadata = []
        if client_call_details.metadata is not None:
            new_metadata = list(client_call_details.metadata)
        new_metadata.extend(self._metadata)

        # Use the named tuple to create new client call details
        return _ClientCallDetails(
            method=client_call_details.method,
            timeout=client_call_details.timeout,
            credentials=client_call_details.credentials,
            metadata=new_metadata,
            wait_for_ready=client_call_details.wait_for_ready,
            compression=client_call_details.compression
        )

# Define a named tuple to represent the client call details
from collections import namedtuple
_ClientCallDetails = namedtuple(
    '_ClientCallDetails',
    ['method', 'timeout', 'credentials', 'metadata', 'wait_for_ready', 'compression']
)

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
        # this will be intercepted by the @wrap_with_error_handler decorator and ignored
        if ServerConnection.is_connection_active():
            raise IgnoredGrpcCallException("Connection already closed; ignoring gRPC call.")
        method_name = client_call_details.method
        self.logger.debug(f"~~~~~~~~~ Outgoing request ~~~~~~~~~")
        self.logger.debug(f"Calling gRPC method: {method_name}")

        start_time = time.perf_counter()
        response = continuation(client_call_details, request)
        self._log_duration(method_name, start_time)
        self._log_response(method_name, response)
        return response

    def _intercept_stream_call(self, continuation, client_call_details, request_iterator):
        # this will be intercepted by the @wrap_with_error_handler decorator and ignored
        if ServerConnection.is_connection_active():
            raise IgnoredGrpcCallException("Connection already closed; ignoring gRPC call.")

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

###########################################################################
#### this provides a central place to handle gRPC errors
###########################################################################
# Custom exception to indicate that the gRPC call should be ignored.
class IgnoredGrpcCallException(Exception):
    pass


def wrap_with_error_handler(method):
    from gRPC_impl.shared_msg_types_pb2 import Empty
    logger = Logger.get_logger()

    def wrapper(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except IgnoredGrpcCallException:  # currently only used for connection close
            return Empty()  # Return a default response or an appropriate response for your method
        except grpc.RpcError as e:
            #import traceback

            #stack_trace = traceback.format_exc()
            server, port = ServerConnection.get_server_ip()
            status_code = e.code()
            logger.error("*** Server error ***")
            logger.error(f"Failed while invoking client method: {method.__module__}.{method.__name__}")
            #logger.error(stack_trace)
            if status_code == grpc.StatusCode.UNAVAILABLE:
                logger.error(f"Please ensure the server is active and reachable.")
                sys.exit(1)
            elif status_code == grpc.StatusCode.INVALID_ARGUMENT:
                logger.error(f"Invalid argument provided to gRPC method {method.__name__}")
                sys.exit(1)
            else:
                logger.error(e.details())
                sys.exit(1)
        except Exception as e:
            if not isinstance(e, grpc.RpcError):  # Ensure it's not a grpc.RpcError
                logger.error(f"Error calling server: {method.__module__}.{method.__name__}")
                logger.error(f"Details: {str(e)}")
                sys.exit(1)

    return wrapper



###########################################################################
#### Handle client kill/end by telling server we are disconnecting
###########################################################################
# this is called when the client is cleanly disconnected
def disconnect():
    try:
        grpc_disconnect()
        Logger.get_logger().info("Disconnected from server.")
    except:
        pass  # Silently handle any errors during disconnect
    finally:
        ServerConnection.close_connection()

@ wrap_with_error_handler
def grpc_disconnect():
    from torch.scaffolding.server_mgmt import client_disconnect
    client_disconnect()

# This is called when the client is forced-quit by the user
def handle_signal(signal, frame):
    Logger.get_logger().info("Forced-quitting; disconnecting from server...")
    disconnect()
    sys.exit(0)

def register_cleanup_handlers():
    # Register signal handlers
    # call disconnect() when the client is forced-quit by the user
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Register atexit function
    # call disconnect() when the client is cleanly disconnected
    Logger.get_logger().info("Client process is exiting; disconnecting from server...")
    atexit.register(disconnect)

