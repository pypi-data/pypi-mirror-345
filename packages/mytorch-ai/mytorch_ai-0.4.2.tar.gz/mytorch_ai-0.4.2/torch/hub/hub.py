###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from proxies.mytorch.hub.hub_proxy import HubProxy
from torch.nn.Module import Module
from torchvision.models import WeightsEnum

# example call: torch.hub.load('pytorch/vision:v0.6.0', 'resnet18', weights=ResNet18_Weights.DEFAULT)
def load(repo: str, model_name: str, weights: WeightsEnum) -> Module:
    model_uuid =  HubProxy().load_module_from_repo(repo, model_name, weights)
    module = Module(uuid=model_uuid)
    return module
