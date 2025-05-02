from gRPC_impl.mytorch.scaffolding import resource_mgmt_pb2_grpc, resource_mgmt_pb2
from connection_utils.server_connection import ServerConnection
from utils.logger import Logger

class ResourceMgmtProxy:
    def __init__(self, grpc_channel):
        self.stub = resource_mgmt_pb2_grpc.ResourceMgmtServiceStub(grpc_channel)
        self.logger = Logger.get_logger()

    def resource_request(self, auth_token: str, client_ip: str, server_id: str, max_time: int):
        request = resource_mgmt_pb2.ResourceRequest()
        request.auth_token = auth_token
        request.client_ip = client_ip
        request.server_id = server_id
        request.max_time = max_time
        response: resource_mgmt_pb2.ResourceRequestResponse = self.stub.resource_request(request)
        self.logger.info(f"Received response from Resource Manager. Resource ID: {response.resource_id if response.resource_id else 'None available'}.")
        # return response as a dictionary
        response_dict = {
            "access_token": response.access_token,
            "additional_info": response.additional_info,
            "resource_id": response.resource_id,
            "resource_ip": response.resource_ip,
            "resource_port": response.resource_port,
            "resource_name": response.resource_name,
            "lease_time": response.lease_time,
            "mytorch_version": response.mytorch_version,
            "resource_info": response.resource_info
        }
        return response_dict
