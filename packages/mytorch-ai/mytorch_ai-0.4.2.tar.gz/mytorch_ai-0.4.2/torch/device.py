###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

"""
This class represents a torch.device object. It is used to specify the device on which a tensor is stored.

A torch.device can be constructed via a string or via a string and device ordinal

Via a string:
    torch.device('cuda:0')
    torch.device('cpu')

Via a string and device ordinal:

    torch.device('cuda', 0)
"""

class device:
    def __init__(self, device_str: str, device_ordinal: int = 0):
        self.device_str = device_str
        self.device_ordinal = device_ordinal

    # overwrite the __str__ method to return the device string
    def __str__(self):
        return self.device_str
