###############################################################################
# Copyright (c) 2024-2025 MyTorch Systems Inc. All rights reserved.
###############################################################################

from proxies.base_proxy import BaseProxy
from utils.logger import Logger
from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from proxies.mytorch.optim.optimizer_proxy import OptimizerProxy


class AdamProxy(OptimizerProxy, BaseProxy):  # Inherit from both
    def __init__(self):
        super().__init__()

        self.logger = Logger.get_logger()
        self.channel = ServerConnection.get_active_connection()
        self.uuid = None  # assigned when optimizer is registered on server

    @wrap_with_error_handler
    def zero_grad(self):
        return self.generic_call("torch.optim", "zero_grad", self.uuid, call_type="method")

    @wrap_with_error_handler
    def step(self):
        return self.generic_call("torch.optim", "step", self.uuid, call_type="method")
    
