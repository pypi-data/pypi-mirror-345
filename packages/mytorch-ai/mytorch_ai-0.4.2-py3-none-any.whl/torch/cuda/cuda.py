###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from proxies.mytorch.cuda.cuda_proxy import CudaProxy
from collections import namedtuple

# The return type of the get_device_properties function is a named tuple
_CudaDeviceProperties = namedtuple('_CudaDeviceProperties', [
    'name', 'total_memory', 'multi_processor_count', 'available_memory', 'allocated_memory',
    'reserved_memory', 'max_memory_allocated', 'max_memory_reserved'
])

def is_available():
    return CudaProxy().is_available()

def empty_cache():
    CudaProxy().empty_cache()

def memory_allocated():
    return CudaProxy().memory_allocated()

def memory_reserved():
    return CudaProxy().memory_reserved()

def get_device_properties(device):
    device_info = CudaProxy().get_device_properties(device)

    # Filter the dictionary to only include keys that are in the namedtuple
    filtered_device_info = {k: v for k, v in device_info.items() if k in _CudaDeviceProperties._fields}

    # Instantiate the namedtuple using ** to unpack the dictionary
    device_properties = _CudaDeviceProperties(**filtered_device_info)
    return device_properties

def get_device_name():
    return CudaProxy().get_device_name()


