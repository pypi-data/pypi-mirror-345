###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

'''
An AutoModel is a generalized factory class that can be used to instantiate a model from a pretrained model.
In almost all cases, a subclass of AutoModel should be used instead of AutoModel itself. Subclasses of AutoModel
are specialized for specific types of models, such as AutoModelForCausalLM for causal language modeling or
AutoModelForSequenceClassification for sequence classification. These subclasses provide additional functionality
and are more user-friendly than AutoModel.
'''

from transformers.PreTrainedModel import PreTrainedModel

class AutoModel(PreTrainedModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
