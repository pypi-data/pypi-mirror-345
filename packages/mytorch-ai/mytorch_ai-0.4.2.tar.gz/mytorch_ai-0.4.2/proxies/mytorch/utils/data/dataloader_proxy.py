###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from torch.utils.data.Dataset import Dataset
from proxies.base_proxy import BaseProxy
from torch.Tensor import Tensor  
from utils.logger import Logger
from connection_utils.server_connection import ServerConnection, wrap_with_error_handler

class DataLoaderProxy(BaseProxy):
    def __init__(self):
        super().__init__()
        self.logger = Logger.get_logger()
        self.channel = ServerConnection.get_active_connection()

    def createDataLoaderOnServer(self, dataset: Dataset, batch_size: int, shuffle: bool):
        self.uuid, dataset_length, batch_size = self.generic_call("torch.utils.data", 
                                                                  "DataLoader", 
                                                                  dataset.uuid, 
                                                                  batch_size, 
                                                                  shuffle,
                                                                  call_type="constructor")
        return self.uuid, dataset_length, batch_size

    def _deserialize_tensor(self, tup):
        """Convert a (uuid, shape, dtype) tuple to a MyTorch Tensor."""
        if isinstance(tup, (list, tuple)) and len(tup) == 3:
            uuid, shape, dtype = tup
            return Tensor(uuid, shape, dtype)
        return tup  # Return raw if it's not a tensor-like tuple

    def __iter__(self):
        """Implements: for batch in dataloader"""
        batches = self.generic_call("torch.utils.data", "__iter__", self.uuid, call_type="method")

        def convert(batch):
            if isinstance(batch, dict):  # Optional support
                return (
                    self._deserialize_tensor(batch.get("inputs")),
                    self._deserialize_tensor(batch.get("targets"))
                )
            if isinstance(batch, (list, tuple)):
                return tuple(self._deserialize_tensor(x) for x in batch)
            return self._deserialize_tensor(batch)

        return iter([convert(batch) for batch in batches])

    def __getitem__(self, index):
        batch = self.generic_call("torch.utils.data", "__getitem__", self.uuid, index)
        if isinstance(batch, (list, tuple)):
            return tuple(self._deserialize_tensor(x) for x in batch)
        return self._deserialize_tensor(batch)

__all__ = ['DataLoaderProxy']
