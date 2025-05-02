###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from torch.Tensor import Tensor
from typing import List, Union
from numpy import ndarray
from PIL import Image
from proxies.mytorchvision.transforms.torchvision_functional_proxy import TorchvisionFunctionalProxy

# same as torchvision.transforms.functional.resize
def resize(img: Tensor, size: List[int]) -> Tensor:
    return TorchvisionFunctionalProxy().resize(img, size)

# same as torchvision.transforms.functional.to_tensor
def to_tensor(pic: Union[Image, ndarray]) -> Tensor:
    return TorchvisionFunctionalProxy().to_tensor(pic)