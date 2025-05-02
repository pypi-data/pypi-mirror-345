###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from torchvision.transforms.Transformer import Transformer
from proxies.mytorchvision.datasets import CIFAR10Proxy
from torch.utils.data.Dataset import Dataset

class CIFAR10(Dataset):
    def __init__(self, root: str, train: bool, download: bool, transform: Transformer):
        super().__init__()
        self.root = root
        self.train = train
        self.download = download
        self.transform = transform
        self.proxy = CIFAR10Proxy(root, train, download, self.transform.uuid)
        self.uuid, self.dataset_length, self.classes = self.createCIFAR10onServer()

    def createCIFAR10onServer(self):
        uuid, dataset_length, classes = self.proxy.createCIFAR10OnServer()
        return uuid, dataset_length, list(classes)

    def __len__(self):
        return self.dataset_length
