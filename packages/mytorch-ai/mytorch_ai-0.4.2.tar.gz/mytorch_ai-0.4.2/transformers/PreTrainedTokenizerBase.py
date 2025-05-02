###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from proxies.mytransformers.HuggingFaceTokenizer_proxy import HuggingFaceTokenizerProxy
from transformers.BatchEncoding import BatchEncoding
from utils.logger import Logger
from utils.spinner import Spinner

class PreTrainedTokenizerBase:
    def __init__(self, uuid=None, special_tokens: dict = None):
        self.uuid = uuid
        self.special_tokens = special_tokens or {}

        # List of special tokens to set as attributes
        token_attributes = [
            'eos_token', 'pad_token', 'bos_token', 'unk_token',
            'sep_token', 'cls_token', 'mask_token'
        ]

        # Set attributes from special_tokens dict
        # e.g. self.eos_token = special_tokens.get('eos_token')
        for attr in token_attributes:
            setattr(self, attr, self.special_tokens.get(attr))

    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path, *inputs, **kwargs):
        Logger.get_logger().info(f"Loading {cls.__name__} for `{pretrained_model_name_or_path}`")
        spinner = Spinner()
        spinner.start()

        try:
            # This method should be implemented by subclasses
            uuid, special_tokens = cls._get_instance_data(pretrained_model_name_or_path, *inputs, **kwargs)
        finally:
            spinner.stop()

        instance = cls(uuid=uuid, special_tokens=special_tokens)
        Logger.get_logger().info(f"...{cls.__name__} has been loaded")
        return instance

    @classmethod
    def _get_instance_data(cls, pretrained_model_name_or_path, *inputs, **kwargs):
        # This method should be implemented by subclasses
        raise NotImplementedError("Subclasses must implement the _get_instance_data method.")

    # Calling tokenizer() is equivalent to calling tokenizer.encode_plus()
    def __call__(self, text, **kwargs):
        return self.encode_plus(text, **kwargs)

    def encode_plus(self, text, **kwargs):
        uuid, data = HuggingFaceTokenizerProxy().encode_plus(self.uuid, text, **kwargs)
        return BatchEncoding(uuid, data)

    def decode(self, input_tensor, **kwargs):
        return HuggingFaceTokenizerProxy().decode(self.uuid, input_tensor.uuid, **kwargs)

    @property
    def pad_token(self):
        return self.pad_token

    # when the value of pad_token is set, we need to update the value on the server
    @pad_token.setter
    def pad_token(self, value):
        HuggingFaceTokenizerProxy().set_pad_token(self.uuid, value)
