###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

# This is an abstract parent class for all datasets in the mytorchvision library.

from utils.logger import Logger

class Dataset:

    def __init__(self):
        self.uuid = None
        self.logger = Logger.get_logger()