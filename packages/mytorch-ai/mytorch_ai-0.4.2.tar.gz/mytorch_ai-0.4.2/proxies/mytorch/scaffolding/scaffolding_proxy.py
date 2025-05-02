from gRPC_impl.mytorch.scaffolding import scaffolding_pb2, scaffolding_pb2_grpc
from gRPC_impl import shared_msg_types_pb2
from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from utils.logger import Logger

class ScaffoldingProxy:
    def __init__(self):
        self.channel = ServerConnection.get_active_connection()
        self.stub = scaffolding_pb2_grpc.ScaffoldingServiceStub(self.channel)
        self.logger = Logger.get_logger()

    @wrap_with_error_handler
    def register_client_with_server(self, client_info: dict):
        # convert the client info dictionary to a protobuf message
        key_value_pairs = [scaffolding_pb2.KeyValuePair(key=key, value=value) for key, value in client_info.items()]
        return self.stub.initialize_client_connection(scaffolding_pb2.ClientInfo(key_value_pairs=key_value_pairs))

    @wrap_with_error_handler
    def get_gpu_info(self):
        return self.stub.get_gpu_info(shared_msg_types_pb2.Empty())
