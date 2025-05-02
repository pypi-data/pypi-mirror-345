###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

'''
Because all of the HuggingFace models have the same API, we can create a single proxy class that can be used to interact with any of them.
'''

from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from gRPC_impl import shared_msg_types_pb2
from gRPC_impl.mytransformers import HuggingFaceModel_pb2_grpc, HuggingFaceModel_pb2
from utils.logger import Logger
from utils.data_transform_utils import convert_grpc_kwargs_to_python, convert_python_to_grpc_kwargs
from torch.Tensor import Tensor

class HuggingFaceModelProxy:

    def __init__(self):
        self.channel = ServerConnection.get_active_connection()
        self.stub = HuggingFaceModel_pb2_grpc.HuggingFaceModelServiceStub(self.channel)
        self.logger = Logger.get_logger()

    @wrap_with_error_handler
    def getAutoModelForSequenceClassification(self, pretrained_model_name_or_path, *model_args, **kwargs):
        request = HuggingFaceModel_pb2.fromPretrained_request(pretrained_model_name_or_path=pretrained_model_name_or_path,
                                                         model_args=model_args,
                                                         kwargs=kwargs)
        response = self.stub.getAutoModelForSequenceClassification(request)
        return response.model_uuid

    @wrap_with_error_handler
    def getAutoModelForCausalML(self, pretrained_model_name_or_path, *model_args, **kwargs):
        # Convert all kwargs values to gRPC Value types
        kwargs_grpc = convert_python_to_grpc_kwargs(kwargs)
        request = HuggingFaceModel_pb2.fromPretrained_request(pretrained_model_name_or_path=pretrained_model_name_or_path,
                                                         model_args=model_args,
                                                         kwargs=kwargs_grpc)
        response = self.stub.getAutoModelForCausalML(request)
        return response.model_uuid

    @wrap_with_error_handler
    def getBertModelForSequenceClassification(self, pretrained_model_name_or_path, *model_args, **kwargs):
        request = HuggingFaceModel_pb2.fromPretrained_request(pretrained_model_name_or_path=pretrained_model_name_or_path,
                                                         model_args=model_args,
                                                         kwargs=kwargs)
        response = self.stub.getBertModelForSequenceClassification(request)
        return response.model_uuid

    @wrap_with_error_handler
    def getRobertaModelForSequenceClassification(self, pretrained_model_name_or_path, *model_args, **kwargs):
        request = HuggingFaceModel_pb2.fromPretrained_request(pretrained_model_name_or_path=pretrained_model_name_or_path,
                                                         model_args=model_args,
                                                         kwargs=kwargs)
        response = self.stub.getRobertaModelForSequenceClassification(request)
        return response.model_uuid

    @wrap_with_error_handler
    def getT5ForConditionalGeneration(self, pretrained_model_name_or_path, *model_args, **kwargs):
        request = HuggingFaceModel_pb2.fromPretrained_request(pretrained_model_name_or_path=pretrained_model_name_or_path,
                                                         model_args=model_args,
                                                         kwargs=kwargs)
        response = self.stub.getT5ForConditionalGeneration(request)
        return response.model_uuid

    @wrap_with_error_handler
    def getAutoModelForSeq2SeqLM(self, pretrained_model_name_or_path, *model_args, **kwargs):
        request = HuggingFaceModel_pb2.fromPretrained_request(pretrained_model_name_or_path=pretrained_model_name_or_path,
                                                         model_args=model_args,
                                                         kwargs=kwargs)
        response = self.stub.getAutoModelForSeq2SeqLM(request)
        return response.model_uuid

    @wrap_with_error_handler
    def getXLNetForSequenceClassification(self, pretrained_model_name_or_path, *model_args, **kwargs):
        request = HuggingFaceModel_pb2.fromPretrained_request(pretrained_model_name_or_path=pretrained_model_name_or_path,
                                                         model_args=model_args,
                                                         kwargs=kwargs)
        response = self.stub.getXLNetForSequenceClassification(request)
        return response.model_uuid

    @wrap_with_error_handler
    def generate(self, model_uuid, **kwargs):
        request = HuggingFaceModel_pb2.generate_request(model_uuid=model_uuid)
        for key, value in kwargs.items():
            if isinstance(value, Tensor):
                request.kwargs.extend([shared_msg_types_pb2.keyValuePair(key=key, string_value=value.uuid)])
            elif isinstance(value, bool):
                request.kwargs.extend([shared_msg_types_pb2.keyValuePair(key=key, bool_value=value)])
            elif isinstance(value, int):
                request.kwargs.extend([shared_msg_types_pb2.keyValuePair(key=key, int_value=value)])
            elif isinstance(value, float):
                request.kwargs.extend([shared_msg_types_pb2.keyValuePair(key=key, float_value=value)])
        response = self.stub.generate(request)
        return response.tensor_uuid