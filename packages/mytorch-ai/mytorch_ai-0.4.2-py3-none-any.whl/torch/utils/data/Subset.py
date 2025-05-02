###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from torch.utils.data.Dataset import Dataset
from typing import Sequence
from proxies.mytorch.utils.data.subset_proxy import SubsetProxy

class Subset(Dataset):
    def __init__(self, dataset: Dataset, indices: Sequence[int]) -> None:
        super().__init__()
        self.dataset = dataset
        self.indices = indices
        self.proxy = SubsetProxy()
        self.uuid, self.dataset_length = self.createSubsetOnServer()

    def createSubsetOnServer(self):
        uuid, dataset_length = self.proxy.createSubsetOnServer(self.dataset, self.indices)
        return uuid, dataset_length

    def __len__(self):
        return self.dataset_length