###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

# Import for direct access
from .mytorch import *

from . import nn
from . import cuda
from . import optim
from . import hub
from . import scaffolding
from . import jit
from . import scaffolding
from .scaffolding import select_server_by_ip, select_server

# Make sure everything is accessible when mytorch is imported as torch
__all__ = ['randn', 'nn', 'from_numpy', 'cuda', 'no_grad', 'optim', 'max', 'Tensor', 'rand',
           'arange', 'meshgrid', 'reshape', 'cat', 'argmax', 'matmul', 'load', 'save', 'hub', 'scaffolding']


# __version__ = "0.1.0" # Initial version; dotplot example
# __version__ = "0.1.5" # ImageFolder infer demo
#__version__ = "0.2.0" # Added Resnet training demo
#__version__ = "0.2.1" # Added uploading data to server during inference (Zynq edge demo)
#__version__ = "0.2.2" # Tracing demo (jit.trace)
#__version__ = "0.2.3" # llama3 CLI demo (Hugging Face transformers library)
#__version__ = "0.2.4" # Pass up client ID to server for data storage
#__version__ = "0.2.5" # Fixed mem leak; --gpu_stats flag
#__version__ = "0.2.6" # Server: multi-client; Client: centralized error handling
#__version__ = "0.2.7" # Basic AWS Neuron support
#__version__ = "0.2.8" # Reorg of grpc_impl
#__version__ = "0.3.0" # Rename to mytorch
#__version__ = "0.3.1" # Added functionality to login to huggingface on the server side
#__version__ = "0.4.0" # Major change due to footbag's generic call supporting anomaly detection
#__version__ = "0.4.1" # Had to increase the required version number of grpc
__version__ = "0.4.2"  # Forgot to modify setup_mytorch.py with new grpc version number
