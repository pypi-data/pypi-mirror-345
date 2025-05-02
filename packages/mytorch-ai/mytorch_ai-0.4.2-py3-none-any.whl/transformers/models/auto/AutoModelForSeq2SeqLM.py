###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

'''
This is a factory class that can be used to instantiate a model for Causal Language Modeling from a pretrained model.
"Causal" refers to the model's ability to predict the next token based only on the previous tokens, not on future tokens.
It's "causal" in the sense that each token can only be influenced by the tokens that came before it, maintaining a cause-effect relationship in the sequence.
'''

from transformers.models.auto.AutoModel import AutoModel
from proxies.mytransformers.HuggingFaceModel_proxy import HuggingFaceModelProxy


class AutoModelForSeq2SeqLM(AutoModel):
    def __init__(self, *args, **kwargs):
        # Call the parent class's __init__ method with the modified kwargs
        super().__init__(*args, **kwargs)

    @classmethod
    def _get_model_uuid(cls, pretrained_model_name_or_path, *args, **kwargs):
        return HuggingFaceModelProxy().getAutoModelForSeq2SeqLM(pretrained_model_name_or_path, *args, **kwargs)
