###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from proxies.mytorch.tensor_proxy import TensorProxy
from utils.data_transform_utils import convert_str_to_numpy_dtype
import numpy as np
from torch.device import device

class Tensor:
    def __init__(self, uuid: str, shape = None, dtype: str = None):
        self.proxy = TensorProxy(uuid)
        self.uuid = uuid

        # if shape not passed in, it will be fetched from the server
        # the first time it is needed
        self._shape = tuple(shape) if shape is not None else None

        # if dtype not passed in, it will be fetched from the server
        # the first time it is needed
        self._dtype = dtype

        # lazy loading of data
        self._retrieved_data = None

    @property
    def shape(self):
        # if shape not passed in, it will be fetched from the server
        # the first time it is needed
        if self._shape is None:
            # Fetch the shape from the server if it hasn't been fetched before
            self._shape = self.proxy.get_shape()
        return self._shape

    @property
    def dtype(self):
        # if dtype not passed in, it will be fetched from the server
        # the first time it is needed
        if self._dtype is None:
            # Fetch the shape from the server if it hasn't been fetched before
            self._dtype = self.proxy.get_dtype()
        return self._dtype

    @property
    def numpy_dtype(self):
       return convert_str_to_numpy_dtype(self.dtype)

    @property
    def retrieved_data(self) -> np.ndarray:
        if self._retrieved_data is None:
            # Assuming TensorProxy.get_data() returns a numpy.ndarray
            self._retrieved_data = self.proxy.get_data()
        return self._retrieved_data

    def size(self, dim = None):
        if dim is None:
            return self.shape
        return self.shape[dim]

    def dim(self):
        return len( self.shape)
    
    def __str__(self):
        return str(self.retrieved_data)

    def __len__(self):
        # Fetch the data shape and return the size of the first dimension
        return self.shape[0]

    def backward(self):
        self.proxy.backward()

    def item(self) -> float:
        return self.proxy.item()

    def float(self):
        uuid, shape, dtype = self.proxy.float()
        return Tensor(uuid, shape, dtype)

    def long(self):
        uuid, shape, dtype = self.proxy.long()
        return Tensor(uuid, shape, dtype)

    def numpy(self):
        return self.retrieved_data

    def cuda(self):
        uuid, shape, dtype = self.proxy.toCuda()
        return Tensor(uuid, shape, dtype)

    def cpu(self):
        uuid, shape, dtype = self.proxy.toCpu()
        return Tensor(uuid, shape, dtype)

    def sum(self, operand):
        uuid, shape, dtype = self.proxy.sum(operand)
        return Tensor(uuid, shape, dtype)
    
    def sub(self, operand):
        #return MyTorchProxy().generic_call("Tensor", "sub", self.uuid, operand)
        uuid, shape, dtype = self.proxy.sub(operand)
        return Tensor(uuid, shape, dtype)

            
    def to(self, device):
        # Convert device object to string if it's not already a string
        device_str = str(device) if not isinstance(device, str) else device
        
        if device_str == "cuda":
            return self.cuda()
        elif device_str == "cpu":
            return self.cpu()
        else:
            raise ValueError(f"Device {device_str} not recognized")

    def reshape(self, shape: tuple):
        uuid, shape, dtype = self.proxy.reshape(shape)
        return Tensor(uuid, shape, dtype)

    def unsqueeze(self, dim):
        uuid, shape, dtype = self.proxy.unsqueeze(dim)
        return Tensor(uuid, shape, dtype)

    def squeeze(self, dim):
        uuid, shape, dtype = self.proxy.squeeze(dim)
        return Tensor(uuid, shape, dtype)

    def view(self, batch_size: int, input_size: int):
        uuid, shape, dtype = self.proxy.view(batch_size, input_size )
        return Tensor(uuid, shape, dtype)

    # transpose
    def t(self):
        uuid, shape, dtype = self.proxy.t()
        return Tensor(uuid, shape, dtype)

    def chunk(self, chunks: int, dim: int = 0):
        """
        Splits the tensor into 'chunks' number of smaller tensors along dimension 'dim'.
        Returns a tuple of new mytorch.Tensor objects.
        """
        # Call the proxy, which returns the uuids, shapes, and dtypes of each chunk
        chunk_info = self.proxy.chunk(chunks, dim)

        # Convert each returned (uuid, shape, dtype) triple into a mytorch.Tensor
        chunk_tensors = []
        for (uuid, shape, dtype) in chunk_info:
            chunk_tensors.append(Tensor(uuid, shape, dtype))

        # PyTorch's chunk returns a tuple, so we'll do the same
        return tuple(chunk_tensors)


    #####################################################################################
    # These methods are needed for the tensor to be treated like a
    # numpy array in some cases, such as with sckit-learn's train_test_split
    #####################################################################################

    # return an actual NumPy array
    def __array__(self, dtype=None):
        return np.asarray(self.retrieved_data, dtype=dtype or self.numpy_dtype)

    # for indexing and slicing
    def __getitem__(self, idx):
        # indexing, e.g. tensor[0]
        if isinstance(idx, int):
            uuid, shape, dtype = self.proxy.index(idx)
            return Tensor(uuid, shape, dtype)

        # slicing, e.g. tensor[0:2,3:,:5]
        else:
            uuid, shape, dtype = self.proxy.slice(idx)
            return Tensor(uuid, shape, dtype)

    # support iteration
    def __iter__(self):
        return iter(self.retrieved_data)

    def __add__(self, other):
        uuid, shape, dtype = self.proxy.add(other.uuid)
        return Tensor( uuid, shape, dtype)

    def __radd__(self, other):
        """Handle case when tensor is on right side of addition."""
        return self.__add__(other)

    def __sub__(self, other):
        uuid, shape, dtype = self.proxy.sub(other.uuid)
        return Tensor( uuid, shape, dtype)

    #def __mul__(self, other):
    #    uuid, shape, dtype = self.proxy.mul(other.uuid)
    #    return Tensor( uuid, shape, dtype)

    def __mul__(self, other):
        operand = other.uuid if isinstance(other, Tensor) else other
        uuid, shape, dtype = self.proxy.mul(operand)
        return Tensor(uuid, shape, dtype)

    def __pow__(self, operand):
        uuid, shape, dtype = self.proxy.pow(operand)
        return Tensor( uuid, shape, dtype)
    
    def __rmul__(self, other):
        return self.__mul__(other)

    # allows for comparison with other tensors
    def __eq__(self, other):
        uuid, shape, dtype =self.proxy.equal(other.uuid)
        return Tensor(uuid, shape, dtype)

    def __del__(self):
        self.proxy.delete()
        pass
