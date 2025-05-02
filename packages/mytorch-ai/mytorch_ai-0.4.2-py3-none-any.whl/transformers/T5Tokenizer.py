###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from .T5TokenizerFast import T5TokenizerFast
from proxies.mytransformers.HuggingFaceTokenizer_proxy import HuggingFaceTokenizerProxy

class T5Tokenizer(T5TokenizerFast):

    def __init__(self, uuid=None, special_tokens: dict = None):
        super().__init__(uuid, special_tokens)

    @classmethod
    def _get_instance_data(cls, pretrained_model_name_or_path, *inputs, **kwargs):
        return HuggingFaceTokenizerProxy().getT5Tokenizer(pretrained_model_name_or_path, *inputs, **kwargs)