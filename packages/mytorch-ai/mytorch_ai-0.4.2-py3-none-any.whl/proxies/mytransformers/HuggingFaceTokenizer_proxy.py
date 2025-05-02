###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

'''
Because all of the HuggingFace tokenizers have the same API, we can create a single proxy class that can be used to interact with any of them.
'''

from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from gRPC_impl import shared_msg_types_pb2
from gRPC_impl.mytransformers import HuggingFaceTokenizer_pb2, HuggingFaceTokenizer_pb2_grpc
from utils.logger import Logger
from torch.Tensor import Tensor

class HuggingFaceTokenizerProxy:

    def __init__(self):
        self.channel = ServerConnection.get_active_connection()
        self.stub = HuggingFaceTokenizer_pb2_grpc.HuggingFaceTokenizerServiceStub(self.channel)
        self.logger = Logger.get_logger()

    @wrap_with_error_handler
    def getAutoTokenizer(self, pretrained_model_name_or_path, *inputs, **kwargs) -> tuple[str, dict]:
        request = HuggingFaceTokenizer_pb2.tokenizerFromPretrained_request(pretrained_model_name_or_path=pretrained_model_name_or_path,
                                                         inputs=inputs,
                                                         kwargs=kwargs)
        response = self.stub.getAutoTokenizer(request)
        special_tokens_dict = dict(response.special_tokens)
        return response.tokenizer_uuid, special_tokens_dict

    @wrap_with_error_handler
    def getBertTokenizer(self, pretrained_model_name_or_path, *inputs, **kwargs) -> tuple[str, dict]:
        request = HuggingFaceTokenizer_pb2.tokenizerFromPretrained_request(pretrained_model_name_or_path=pretrained_model_name_or_path,
                                                         inputs=inputs,
                                                         kwargs=kwargs)
        response = self.stub.getBertTokenizer(request)
        special_tokens_dict = dict(response.special_tokens)
        return response.tokenizer_uuid, special_tokens_dict

    @wrap_with_error_handler
    def getRobertaTokenizer(self, pretrained_model_name_or_path, *inputs, **kwargs) -> tuple[str, dict]:
        request = HuggingFaceTokenizer_pb2.tokenizerFromPretrained_request(pretrained_model_name_or_path=pretrained_model_name_or_path,
                                                         inputs=inputs,
                                                         kwargs=kwargs)
        response = self.stub.getRobertaTokenizer(request)
        special_tokens_dict = dict(response.special_tokens)
        return response.tokenizer_uuid, special_tokens_dict

    @wrap_with_error_handler
    def getT5Tokenizer(self, pretrained_model_name_or_path, *inputs, **kwargs) -> tuple[str, dict]:
        request = HuggingFaceTokenizer_pb2.tokenizerFromPretrained_request(pretrained_model_name_or_path=pretrained_model_name_or_path,
                                                         inputs=inputs,
                                                         kwargs=kwargs)
        response = self.stub.getT5Tokenizer(request)
        special_tokens_dict = dict(response.special_tokens)
        return response.tokenizer_uuid, special_tokens_dict

    @wrap_with_error_handler
    def getXLNetTokenizer(self, pretrained_model_name_or_path, *inputs, **kwargs) -> tuple[str, dict]:
        request = HuggingFaceTokenizer_pb2.tokenizerFromPretrained_request(pretrained_model_name_or_path=pretrained_model_name_or_path,
                                                         inputs=inputs,
                                                         kwargs=kwargs)
        response = self.stub.getXLNetTokenizer(request)
        special_tokens_dict = dict(response.special_tokens)
        return response.tokenizer_uuid, special_tokens_dict

    @wrap_with_error_handler
    def encode_plus(self, tokenizer_uuid, text, **kwargs):
        request = HuggingFaceTokenizer_pb2.encodePlus_request(tokenizer_uuid=tokenizer_uuid, text=text)
        for key, val in kwargs.items():
            # value can be a string, int, float, or bool
            if isinstance(val, str):
                request.kwargs.extend([shared_msg_types_pb2.keyValuePair(key=key, string_value=val)])
            elif isinstance(val, bool):
                request.kwargs.extend([shared_msg_types_pb2.keyValuePair(key=key, bool_value=val)])
            elif isinstance(val, int):
                request.kwargs.extend([shared_msg_types_pb2.keyValuePair(key=key, int_value=val)])
            elif isinstance(val, float):
                request.kwargs.extend([shared_msg_types_pb2.keyValuePair(key=key, float_value=val)])
        response = self.stub.encode_plus(request)
        # convert the response.data to a dictionary
        data = {}
        for pair in response.data:
            tensor = Tensor(uuid=pair.tensor_uuid)
            data[pair.key] = tensor
        return response.encoding_uuid, data

    @wrap_with_error_handler
    def decode(self, tokenizer_uuid, input_tensor_uuid, **kwargs):
        request = HuggingFaceTokenizer_pb2.decode_request(tokenizer_uuid=tokenizer_uuid, input_tensor_uuid=input_tensor_uuid)
        for key, val in kwargs.items():
            # value can be a string, int, float, or bool
            if isinstance(val, str):
                request.kwargs.extend([shared_msg_types_pb2.keyValuePair(key=key, string_value=val)])
            elif isinstance(val, bool):
                request.kwargs.extend([shared_msg_types_pb2.keyValuePair(key=key, bool_value=val)])
            elif isinstance(val, int):
                request.kwargs.extend([shared_msg_types_pb2.keyValuePair(key=key, int_value=val)])
            elif isinstance(val, float):
                request.kwargs.extend([shared_msg_types_pb2.keyValuePair(key=key, float_value=val)])
        response = self.stub.decode(request)
        return response.text

    @wrap_with_error_handler
    def set_pad_token(self, tokenizer_uuid, value):
        request = HuggingFaceTokenizer_pb2.setPadToken_request(tokenizer_uuid=tokenizer_uuid, pad_token=value)
        self.stub.set_pad_token(request)
        return