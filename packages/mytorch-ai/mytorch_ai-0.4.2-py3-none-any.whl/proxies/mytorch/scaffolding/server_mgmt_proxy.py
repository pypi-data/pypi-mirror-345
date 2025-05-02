from gRPC_impl.mytorch.scaffolding import server_mgmt_pb2, server_mgmt_pb2_grpc
from gRPC_impl import shared_msg_types_pb2
from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from utils.logger import Logger

class ServerMgmtProxy:
    def __init__(self):
        self.channel = ServerConnection.get_active_connection()
        self.stub = server_mgmt_pb2_grpc.ServerMgmtServiceStub(self.channel)
        self.logger = Logger.get_logger()

    @wrap_with_error_handler
    def server_status(self) -> str:
        response: server_mgmt_pb2.ServerStatus = self.stub.server_status(shared_msg_types_pb2.Empty())
        return response.server_status

    # called when the client disconnects: either gracefully or due to an error or forceful termination
    def client_disconnect(self):
        self.stub.client_disconnect(shared_msg_types_pb2.Empty())

    def get_server_gpu_stats(self) -> [dict]:
        response: server_mgmt_pb2.GpuInfoList = self.stub.get_server_gpu_stats(shared_msg_types_pb2.Empty())
        gpu_stats = []
        for gpu_info_dict in response.gpu_dicts:
            gpu_stats.append(gpu_info_dict.items)
        return gpu_stats