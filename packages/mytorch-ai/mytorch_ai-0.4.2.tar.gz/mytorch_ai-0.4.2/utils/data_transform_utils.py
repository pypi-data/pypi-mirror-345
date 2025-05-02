###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

"""
This proxy provides utility methods for deserializing tensors and state_dicts.

"""

import numpy as np
from gRPC_impl import shared_msg_types_pb2

def convert_str_to_numpy_dtype(dtype_str) -> np.dtype:
    """Converts a dtype string from PyTorch format to NumPy dtype."""
    dtype_map = {
        'torch.float32': np.float32,
        'torch.float64': np.float64,
        'torch.float16': np.float16,
        'torch.int32': np.int32,
        'torch.int64': np.int64,
        'torch.int16': np.int16,
        'torch.int8': np.int8,
        'torch.uint8': np.uint8,
    }
    return dtype_map.get(dtype_str, np.float32)  # Default to np.float32 if not found

def deserialize_tensor(tensor_data, tensor_shape, dtype_str) -> np.ndarray:
    """Deserializes tensor data (bytes) into a NumPy array."""
    dtype: np.dtype = convert_str_to_numpy_dtype(dtype_str)  # Use the utility method to convert dtype
    shape_tuple = tuple(tensor_shape) # Convert the RepeatedScalarContainer of the gRPC data to a tuple
    return np.frombuffer(tensor_data, dtype=dtype).reshape(shape_tuple)

def deserialize_state_dict(serialized_state_dict) -> dict:
    """Deserializes a serialized state_dict (protobuf message) into a dictionary of NumPy arrays."""
    state_dict_np = {}
    for param_name, serialized_tensor in serialized_state_dict.entries.items():
        tensor_np = deserialize_tensor(serialized_tensor.data,
                                       serialized_tensor.shape,
                                       dtype_str=serialized_tensor.dtype)
        state_dict_np[param_name] = tensor_np
    return state_dict_np

def serialize_numpy_array(np_array: np.ndarray) -> shared_msg_types_pb2.SerializedNumpyArray:
    array_data = np_array.tobytes()
    array_shape = list(np_array.shape)
    array_dtype = str(np_array.dtype)
    return shared_msg_types_pb2.SerializedNumpyArray(
            data=array_data,
            shape=array_shape,
            dtype=array_dtype
        )

def convert_python_to_grpc_value(value):
    grpc_value = shared_msg_types_pb2.Value()
    if isinstance(value, bool):
        grpc_value.bool_value = value
    elif isinstance(value, int):
        grpc_value.int_value = value
    elif isinstance(value, float):
        grpc_value.float_value = value
    elif isinstance(value, str):
        grpc_value.string_value = value
    else:
        grpc_value.string_value = str(value)
    return grpc_value

def convert_python_to_grpc_kwargs(kwargs):
    return {k: convert_python_to_grpc_value(v) for k, v in kwargs.items()}

def convert_grpc_value_to_python(value):
    # If it's already a Python primitive type, return it directly
    if isinstance(value, (str, int, float, bool)):
        return value
        
    # Otherwise handle gRPC Value type
    which_oneof = value.WhichOneof('kind')
    if which_oneof == 'string_value':
        return value.string_value
    elif which_oneof == 'int_value':
        return value.int_value
    elif which_oneof == 'float_value':
        return value.float_value
    elif which_oneof == 'bool_value':
        return value.bool_value
    return None

def convert_grpc_kwargs_to_python(kwargs):
    # Convert the entire kwargs dictionary
    python_kwargs = {
        key: convert_grpc_value_to_python(value) 
        for key, value in kwargs.items()
    }
    return python_kwargs
