###############################################################################
# Copyright (c) 2025 MyTorch Systems Inc. All rights reserved.
###############################################################################
#from torch.nn.Module import Module
#from proxies.mytorch.mytorch_proxy import MyTorchProxy
#from torch.Tensor import Tensor
from proxies.mytorch.nn.layers_proxy import SigmoidProxy

class Sigmoid:
    
    def __init__(self):
        self.proxy = SigmoidProxy()

    def __call__(self, tensor):
        # Delegate the call to SigmoidProxy for execution
        return self.proxy.forward(tensor)
