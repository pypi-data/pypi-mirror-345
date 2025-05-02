###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from torch.nn.Module import Module
from utils.logger import Logger
from proxies.mytransformers.HuggingFaceModel_proxy import HuggingFaceModelProxy
from torch.Tensor import Tensor
from utils.spinner import Spinner

class PreTrainedModel(Module):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = Logger.get_logger()

    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path, *args, **kwargs):
        Logger.get_logger().info(f"Loading {cls.__name__} model `{pretrained_model_name_or_path}`")
        spinner = Spinner()
        spinner.start()

        try:
            # This method should be implemented by subclasses
            model_uuid = cls._get_model_uuid(pretrained_model_name_or_path, *args, **kwargs)
        finally:
            spinner.stop()

        model = cls(uuid=model_uuid)  # calls the class's __init__ method
        Logger.get_logger().info(f"...model has been loaded")
        return model

    @classmethod
    def _get_model_uuid(cls, pretrained_model_name_or_path, *args, **kwargs):
        # This method should be implemented by subclasses
        raise NotImplementedError("Subclasses must implement the _get_model_uuid method.")


    def generate(self, **kwargs):
        tensor_uuid = HuggingFaceModelProxy().generate(self.uuid, **kwargs)
        return Tensor(uuid=tensor_uuid)