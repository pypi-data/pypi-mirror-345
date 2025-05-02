###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

# For now, parent class for all the transforms such as CenterCrop, Resize, etc.
# //TODO: tranforms should be a subclass of nn.Module

class Transformer:
    def __init__(self):
        self.uuid = None