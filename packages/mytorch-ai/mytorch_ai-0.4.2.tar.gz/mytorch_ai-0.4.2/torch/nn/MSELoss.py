###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from proxies.base_proxy import BaseProxy
from torch.Tensor import Tensor
from connection_utils.server_connection import ServerConnection

class MSELoss:
    def __init__(self, reduction="mean"):
        self.reduction = reduction
        self.proxy = BaseProxy()
        self.proxy.channel = ServerConnection.get_active_connection()
        self.uuid = self.proxy.generic_call(
            "torch.nn", "MSELoss",
            call_type="constructor",
            kwargs={"reduction": self.reduction}
        )
    def __call__(self, input: Tensor, target: Tensor):
        uuid, shape, dtype = self.proxy.generic_call(
            "torch.nn", "forward",
            self.uuid, input.uuid, target.uuid,
            call_type="forward"
        )
        return Tensor(uuid, shape, dtype)
