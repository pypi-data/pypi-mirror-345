###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from torchvision.models.weight_enums import WeightsEnum
from proxies.mytorchvision.models.ModelsProxy import ModelsProxy
from torch.nn.Module import Module

# example call: torchvision.models.resnet18(weights=ResNet18_Weights.DEFAULT)
def resnet18(weights: WeightsEnum) -> Module:
    model_uuid =  ModelsProxy().resnet18(weights)
    module = Module(uuid=model_uuid)
    return module

def resnet50(weights: WeightsEnum) -> Module:
    model_uuid =  ModelsProxy().resnet50(weights)
    module = Module(uuid=model_uuid)
    return module

def resnet152(weights: WeightsEnum) -> Module:
    model_uuid =  ModelsProxy().resnet152(weights)
    module = Module(uuid=model_uuid)
    return module