###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

'''
This is a factory class that can be used to instantiate a Bert model for sequence classification from a pretrained model.
'''

from transformers.PreTrainedModel import PreTrainedModel
from proxies.mytransformers.HuggingFaceModel_proxy import HuggingFaceModelProxy

class T5ForConditionalGeneration(PreTrainedModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def _get_model_uuid(cls, pretrained_model_name_or_path, *args, **kwargs):
        return HuggingFaceModelProxy().getT5ForConditionalGeneration(pretrained_model_name_or_path, *args, **kwargs)
