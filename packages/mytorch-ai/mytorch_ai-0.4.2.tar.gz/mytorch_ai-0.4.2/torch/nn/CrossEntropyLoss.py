###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from proxies.mytorch.nn.loss_function_proxy import LossFunctionProxy
from torch.Tensor import Tensor

class CrossEntropyLoss:
    def __init__(self):
        self.proxy = LossFunctionProxy.create_CrossEntropyLoss()

    # this makes the object 'callable' so that it can be used as a function.
    # For example, we can call `loss_function(input_data, target)` to compute the loss.
    def __call__(self, input_data, target) -> Tensor:
        return self.proxy.run_loss(input_data, target)
