###############################################################################
# Copyright (c) 2018-2019 MyTorch Systems Inc. All rights reserved.
###############################################################################
"""
This file contains a NoOpContextManager class that is used when we want
to execute a block of code with no side effects. This is useful when we
want to use a with statement to execute a block of code such as:

    with torch.no_grad():
        blah
        blah
        blah

"""

class NoOpContextManager:
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
