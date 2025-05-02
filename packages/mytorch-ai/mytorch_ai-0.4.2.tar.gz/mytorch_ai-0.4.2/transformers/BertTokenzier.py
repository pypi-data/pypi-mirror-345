###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from .BertTokenizerFast import BertTokenizerFast
from proxies.mytransformers.HuggingFaceTokenizer_proxy import HuggingFaceTokenizerProxy

class BertTokenizer(BertTokenizerFast):

    def __init__(self, uuid=None, special_tokens: dict = None):
        super().__init__(uuid, special_tokens)

    @classmethod
    def _get_instance_data(cls, pretrained_model_name_or_path, *inputs, **kwargs):
        return HuggingFaceTokenizerProxy().getBertTokenizer(pretrained_model_name_or_path, *inputs, **kwargs)