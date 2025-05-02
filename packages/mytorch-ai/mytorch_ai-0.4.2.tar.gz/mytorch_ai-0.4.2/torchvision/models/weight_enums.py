from enum import Enum, unique

@unique
class WeightsEnum(Enum):
    DEFAULT = 0
    IMAGENET1K_V1 = 1
    IMAGENET1K_V2 = 2

# Dynamically create a new Enum that includes all members from WeightsEnum
# and potentially adds new ones
ResNet18_Weights = Enum('ResNet18_Weights', [(name, member.value) for name, member in WeightsEnum.__members__.items()])
ResNet50_Weights = Enum('ResNet50_Weights', [(name, member.value) for name, member in WeightsEnum.__members__.items()])
ResNet152_Weights = Enum('ResNet152_Weights', [(name, member.value) for name, member in WeightsEnum.__members__.items()])