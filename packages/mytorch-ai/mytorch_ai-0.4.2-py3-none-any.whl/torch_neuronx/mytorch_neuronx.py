###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from proxies.mytorch_neuronx.mytorch_neuronx_proxy import CqtorchNeuronxProxy
from torch.Tensor import Tensor
from torch.nn.Module import Module

'''
FROM: help(torch_neuronx.trace)
Help on function trace in module torch_neuronx.xla_impl.trace:

trace(func: Union[Callable, torch.nn.modules.module.Module], 
        example_inputs: Any, *_,  <-- must be same dimensions as the input(s) you will pass to the model
        input_output_aliases: Dict = {}, 
        compiler_workdir: Union[str, pathlib.Path, NoneType] = None, 
        compiler_args: Union[List[str], str, NoneType] = None, 
        partitioner_config: Optional[torch_neuronx.xla_impl.partitioner.PartitionerConfig] = None, 
        inline_weights_to_neff=True, **kwargs) 
        -> torch.jit._script.ScriptModule
    Trace a torch module/function to produce a compiled Neuron ScriptModule.
    
    This uses torch-xla to extract the computation graph. The input `func` and
    `example_inputs` must be able to be moved to the XLA device.
    
    The resulting module can used with `torch.jit.save` and `torch.jit.load`
    
    NOTE: Please use keyword arguments for all arguments after `example_inputs`.
    Ex: `torch_neuronx.trace(func,example_inputs,compiler_workdir="some_dir") #valid`
        `torch_neuronx.trace(func,example_inputs,"some_dir") #invalid`
    
    Args:
        func: A module or function which defines a torch model or computation.
        example_inputs: An example set of inputs which will be passed to the
            `func` during tracing.
        input_output_aliases: alias mapping between the inputs and outputs
        compiler_workdir: The directory to save any compiler outputs to.
        compiler_args: Additional compiler arguments.
        partitioner_config: A PartitionerConfig object, which can be optionally
        supplied if there are unsupported ops in the model that need to be
        partitioned out to CPU.
        inline_weights_to_neff: A boolean indicating whether the weights should be
        inlined to the neff. The default is `True`.
    
    Returns:
        A Module where the HLO computation is a fused neuron::foward operation.
'''
def trace(model:Module, example_inputs: tuple[Tensor, ...]):
    model_uuid =  CqtorchNeuronxProxy().trace(model, example_inputs)
    return Module(uuid=model_uuid)