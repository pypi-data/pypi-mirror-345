###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
from torchvision.transforms.Transformer import Transformer
from proxies.mytorchvision.datasets.ImageFolderProxy import ImageFolderProxy
import torch.scaffolding.data_mgmt as data_mgmt
from torch.Tensor import Tensor
from torch.utils.data.Dataset import Dataset
from utils.MyTorchClient import MyTorchClient
from typing import Optional
import os

"""
The ImageFolder dataset class is a generic data loader where the images are arranged in this way:
root/dog/xxx.png
root/dog/xxy.png
root/dog/xxz.png
root/cat/123.png
root/cat/nsdf3.png
root/cat/asd932_.png

where 'dog', 'cat' are the class labels. The class labels are determined by the folder structure of the dataset.

The `datapath` can either be a path on the client or on the server. If it is on the client but not on the server,
the data will be uploaded to the server. If it is on the server, the data will be used from there (unless the 
OVERRIDE_SERVER_DATA flag is set).

If the datapath parameter is absolute, it will be assumed to be pointing to a directory on the client, as all server paths 
are relative to the server's data directory (which is set in the server code). In this case, the final folder in the full path will be
uploaded to the server. For example, if the datapath is /home/user/data/resnet, only the 'resnet' folder will be uploaded
to the server's data directory, where the folder `resnet` and any subdirectories will be created. However, if the folder
`resnet` already exists on the server, the data will not be uploaded again.

...Thus, ImageFolder('/home/user/data/resnet', transform) 
    - if folder does not exist on client:
        - raise FileNotFoundError
    - if folder exists on client:
        - see if folder `resnet` already exists on the server
            - if not, upload the 'resnet' folder to the server's data directory.


If the datapath parameter is relative, we will to see if the folder exists on the server (relative to the server's data
directory), and on the client (relative to the directory that contains the running scriopt). 
If the contents already exist on the server (and the OVERRIDE_SERVER_DATA flag is not set), the data will not be uploaded again.
If the contents do not exist on the server, the data will be uploaded to the server. Only the final folder in the relative path
will be uploaded to the server's data directory. For example, if the datapath is '../data/resnet', only the 'resnet' folder will be
uploaded to the server's data directory, where the folder `resnet` and any subdirectories will be created.

...Thus, ImageFolder('../data/resnet', transform)
    - if folder `resnet` already exists on the server
        - if yes, no data will be uploaded
    - else if folder exists on client:
        - upload the 'resnet' folder to the server's data directory.
    - if folder does not exist on client:
        - raise FileNotFoundError

"""

class ImageFolder(Dataset):
    def __init__(self, datapath: str, transform: Optional[Transformer] = None):
        super().__init__()
        self.datapath = datapath
        self.trailing_folder = os.path.basename(self.datapath)
        self.transform = transform
        self.proxy = ImageFolderProxy()
        # if no transform is provided, set transform_uuid to an empty string
        self.transform_uuid = self.transform.uuid if self.transform is not None else ""
        trailing_folder = os.path.basename(self.datapath) # e.g. 'resnet' if datapath is '/home/user/data/resnet'
        self.uuid, self.tuple_list, self.classes = self.createImageFolderOnServer()
        self.imgs = [img for img, label in self.tuple_list]
        self.targets = [label for img, label in self.tuple_list]

    def createImageFolderOnServer(self):
        if self.must_upload_data():
            # see if folder exists on the client
            if not os.path.exists(self.datapath):
                raise FileNotFoundError(f"Path `{self.datapath}` does not exist on the client")
            data_mgmt.upload_folder_to_server(self.datapath)

        image_folder_uuid, image_uuids, labels, classes = self.proxy.createImageFolderOnServer(self.trailing_folder, self.transform_uuid)
        # we want to generate a tuple list, where the tuple is (mytorch.Tensor, label)
        tuple_list =  [(Tensor(image_uuid), label) for image_uuid, label in zip(image_uuids, labels)]
        self.logger.info(f"ImageFolder with data from `{self.trailing_folder}` created with {len(tuple_list)} images.")
        return image_folder_uuid, tuple_list, classes

    def must_upload_data(self):
        if MyTorchClient.instance().get_overwrite_server_data():
            self.logger.info("OVERRIDE_SERVER_DATA flag is set. Uploading data to server.")
            return True

        if os.path.isabs(self.datapath): # if the datapath is absolute
            # see if folder exists on the client
            if not os.path.exists(self.datapath):
                raise FileNotFoundError(f"Path `{self.datapath}` does not exist on the client")
            # check if the folder exists on the server
            if data_mgmt.folder_exists_on_server(self.trailing_folder):
               self.logger.info(f"Data folder {self.trailing_folder} already exists on the server, no data will be uploaded")
               return False
            return True

        else: # if the datapath is relative
            on_server = data_mgmt.folder_exists_on_server(self.trailing_folder)
            if on_server:
                self.logger.info(f"Data folder `{self.trailing_folder}` already exists on the server, no data will be uploaded")
                return False
            # see if folder exists on the client
            if not os.path.exists(self.datapath):
                raise FileNotFoundError(f"Path `{self.datapath}` does not exist on the client")
            return True

    # for indexing, e.g. image_folder[0]
    def __getitem__(self, idx):
        # return index of self.tuple_list
        return self.tuple_list[idx]

    def __array__(self):
        return self.tuple_list

    # support iteration
    def __iter__(self):
        return iter(self.tuple_list)

    def __len__(self):
        # Return the length of the internal array
        return len(self.tuple_list)
