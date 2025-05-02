###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from proxies.mytorch.scaffolding.server_mgmt_proxy import ServerMgmtProxy
from connection_utils.server_connection import ServerConnection
from utils.logger import Logger

def server_status() -> str:
    if ServerConnection.is_connection_active():
        return ServerMgmtProxy().client_disconnect()
    else:
        return

def client_disconnect() -> None:
    Logger.get_logger().info("Disconnecting from server...")
    return ServerMgmtProxy().client_disconnect()

def print_server_gpu_stats() -> None:
    info_list = ServerMgmtProxy().get_server_gpu_stats()
    for index, info_dict in enumerate(info_list):
        print(f"~~~ GPU {index} ~~~")
        # print info_dict
        for key, value in info_dict.items():
            print(f"{key}: {value}")