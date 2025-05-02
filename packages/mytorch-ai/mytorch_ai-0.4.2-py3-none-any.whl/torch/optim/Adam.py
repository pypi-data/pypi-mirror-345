###############################################################################
# Copyright (c) 2024-2025 MyTorch Systems Inc. All rights reserved.
###############################################################################

from proxies.mytorch.optim.adam_proxy import AdamProxy
from typing import Iterable, Dict, Any, Tuple, Union, Optional
from torch.Tensor import Tensor
from typing_extensions import TypeAlias

ParamsT: TypeAlias = Union[
    Iterable[Tensor], Iterable[Dict[str, Any]], Iterable[Tuple[str, Tensor]]
]

class Adam:
    def __init__(
        self,
        params: ParamsT,
        lr: Union[float, Tensor] = 1e-3,
        betas: Tuple[Union[float, Tensor], Union[float, Tensor]] = (0.9, 0.999),
        eps: float = 1e-8,
        weight_decay: float = 0,
        amsgrad: bool = False,
        *,
        foreach: Optional[bool] = None,
        maximize: bool = False,
        capturable: bool = False,
        differentiable: bool = False,
        fused: Optional[bool] = None,
        ):
            self.proxy = AdamProxy()

            param_uuids = []
            for p in params:
                if hasattr(p, 'uuid'):
                    param_uuids.append(p.uuid)
                else:
                    raise TypeError(f"Adam received a non-proxied parameter: {p}")

            self.proxy.uuid = self.proxy.generic_call(
                "torch.optim", "Adam",
                param_uuids,  
                call_type="constructor",
                kwargs={
                    "lr": lr,
                    "betas": betas,
                    "eps": eps,
                    "weight_decay": weight_decay,
                    "amsgrad": amsgrad,
                    "foreach": foreach,
                    "maximize": maximize,
                    "capturable": capturable,
                    "differentiable": differentiable,
                    "fused": fused
                }
            )


    def zero_grad(self):
        return self.proxy.zero_grad()

    def step(self):
        return self.proxy.step()