###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

class BatchEncoding:
    def __init__(self, uuid, data_dict):
        self.uuid = uuid
        self.data = data_dict # {string: Tensor}

    # have the ability to access the data dictionary as if it were an attribute
    def __getitem__(self, key):
        return self.data[key]

    def items(self):
        return self.data.items()

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def get(self, key, default=None):
        return self.data.get(key, default)

    def __contains__(self, key):
        return key in self.data

    def to_dict(self):
        return dict(self.data)