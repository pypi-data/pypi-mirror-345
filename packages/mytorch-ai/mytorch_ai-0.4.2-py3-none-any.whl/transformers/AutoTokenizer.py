###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

'''
An AutoTokenizer is a generalized factory class that can be used to instantiate a tokenizer from a pretrained model.

For example, calling AutoTokenizer.from_pretrained(pretrained_model_name_or_path) given a BERT model name or path
is the same as calling BertTokenizer.from_pretrained(pretrained_model_name_or_path).
'''

from proxies.mytransformers.HuggingFaceTokenizer_proxy import HuggingFaceTokenizerProxy
from transformers.PreTrainedTokenizerBase import PreTrainedTokenizerBase

class AutoTokenizer(PreTrainedTokenizerBase):

    def __init__(self, uuid=None, special_tokens: dict = None):
        super().__init__(uuid, special_tokens)

    @classmethod
    def _get_instance_data(cls, pretrained_model_name_or_path, *inputs, **kwargs):
        return HuggingFaceTokenizerProxy().getAutoTokenizer(pretrained_model_name_or_path, *inputs, **kwargs)