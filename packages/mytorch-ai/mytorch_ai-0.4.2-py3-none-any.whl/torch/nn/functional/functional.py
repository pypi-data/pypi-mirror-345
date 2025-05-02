###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from proxies.mytorch.nn.functional.functional_proxy import FunctionalProxy
from torch.Tensor import Tensor

def softmax(input: Tensor, dim: int) -> Tensor:
    proxy = FunctionalProxy()
    return proxy.softmax(input, dim)

#def relu(input: Tensor, inplace: bool = False) -> Tensor:
#    proxy = FunctionalProxy()
#    return proxy.relu(input, inplace)