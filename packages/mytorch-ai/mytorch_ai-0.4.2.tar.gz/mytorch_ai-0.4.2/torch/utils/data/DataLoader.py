###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from torch.utils.data.Dataset import Dataset
from proxies.mytorch.utils.data.dataloader_proxy import DataLoaderProxy

class DataLoader:
    def __init__(self, dataset: Dataset, batch_size: int, shuffle: bool) -> None:
        super().__init__()
        self.dataset = dataset
        self.shuffle = shuffle
        self.proxy = DataLoaderProxy()
        self.uuid, self.dataset_length, self.batch_size = self.createDataLoaderOnServer(dataset, batch_size, shuffle)
        self.batch_index = 0  # Initialize batch index

    def createDataLoaderOnServer(self, dataset: Dataset, batch_size: int, shuffle: bool):
        uuid, dataset_length, batch_size = self.proxy.createDataLoaderOnServer(dataset, batch_size, shuffle)
        return uuid, dataset_length, batch_size
    
    def __len__(self):
        return self.dataset_length

    def __iter__(self):
        """
        Makes the DataLoader iterable. The proxy returns a list of (input, target) tuples.
        """
        return iter(self.proxy)

    def __getitem__(self, index):
        """
        Direct indexing of batches. Returns a tuple (inputs, targets).
        """
        return self.proxy[index]

# Export everything from this module
__all__ = ['DataLoader']
