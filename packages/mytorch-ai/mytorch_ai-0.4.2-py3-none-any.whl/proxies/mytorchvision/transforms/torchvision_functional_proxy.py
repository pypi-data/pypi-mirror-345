###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from torch.Tensor import Tensor
from typing import List, Union
from numpy import ndarray
from PIL import Image
from utils.logger import Logger
from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from gRPC_impl.mytorchvision.transforms import torchvision_functional_pb2, torchvision_functional_pb2_grpc
from gRPC_impl import shared_msg_types_pb2
import numpy as np
from utils import data_transform_utils

class TorchvisionFunctionalProxy:
    def __init__(self):
        self.channel = ServerConnection.get_active_connection()
        self.stub = torchvision_functional_pb2_grpc.TorchvisionFunctionalServiceStub(self.channel)
        self.logger = Logger.get_logger()

    # same as torchvision.transforms.functional.resize
    @wrap_with_error_handler
    def resize(self, img: Tensor, size: List[int]) -> Tensor:
        request = torchvision_functional_pb2.ResizeRequest()
        request.tensor_uuid = img.uuid
        request.size.extend(size)
        response: shared_msg_types_pb2.GrpcTensor = self.stub.resize(request)
        return Tensor(response.uuid, response.shape, response.dtype)

    # same as torchvision.transforms.functional.to_tensor
    @wrap_with_error_handler
    def to_tensor(self, pic: Union[Image, ndarray]) -> Tensor:
        if isinstance(pic, Image.Image):
            np_array = np.array(pic)
        else:
            np_array = pic
        request: shared_msg_types_pb2.SerializedNumpyArray = data_transform_utils.serialize_numpy_array(np_array)
        response: shared_msg_types_pb2.GrpcTensor = self.stub.to_tensor(request)
        return Tensor(response.uuid, response.shape, response.dtype)