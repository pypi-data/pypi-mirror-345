###############################################################################
# Copyright (c) 2024-2025 MyTorch Systems Inc. All rights reserved.
###############################################################################
from torch.utils.data.Dataset import Dataset
from torch.Tensor import Tensor
from typing import Tuple, Sequence
from proxies.mytorch.utils.data.tensordataset_proxy import TensorDatasetProxy


class TensorDataset(Dataset):
    def __init__(self, dataset: Dataset) -> None:
        super().__init__()
        self.dataset = dataset
        self.proxy = TensorDatasetProxy()
        self.uuid, self.dataset_length = self.createTensorDatasetOnServer()

    def createTensorDatasetOnServer(self):
        uuid, dataset_length = self.proxy.createTensorDatasetOnServer(self.dataset)
        return uuid, dataset_length

    def __len__(self):
        return self.dataset_length
