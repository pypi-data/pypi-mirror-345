###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from proxies.mytorch.optim.optimizer_proxy import OptimizerProxy
from torch.nn.ParametersGenerator import ParametersGenerator

class SGD:
    def __init__(self, generator: ParametersGenerator, lr: float, momentum: float = 0):
        self.proxy = OptimizerProxy()
        self.uuid = self.proxy.create_SGD(generator.uuid, lr, momentum)
        self.proxy.uuid = self.uuid

    def zero_grad(self):
        self.proxy.zero_grad()

    def step(self):
        self.proxy.step()