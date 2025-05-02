###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from proxies.mytorch.scaffolding.data_mgmt_proxy import DataMgmtProxy

def folder_exists_on_server(folder_path: str) -> bool:
    return DataMgmtProxy().folder_exists_on_server(folder_path)

def upload_folder_to_server(folder_path: str) -> int:
    return DataMgmtProxy().upload_folder(folder_path)