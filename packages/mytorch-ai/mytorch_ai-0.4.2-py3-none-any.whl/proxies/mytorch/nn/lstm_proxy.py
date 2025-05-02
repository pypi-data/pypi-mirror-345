###############################################################################
# File: mytorch/client/proxies/mytorch/nn/lstm_proxy.py
###############################################################################
"""
Proxy that represents a server-side LSTM “Module.”
We store an LSTM on the server via generic_call(…).
"""
from proxies.mytorch.nn.module_proxy import ModuleProxy
from torch.Tensor import Tensor

class LSTMProxy(ModuleProxy):
    """
    Re-uses all the “ModuleProxy” logic so it can store parameters, do forward, etc.
    """

    def create_lstm_on_server(self, input_size, hidden_size, num_layers, bias,
                              batch_first, dropout, bidirectional):
        """
        Tells the server to create a real torch.nn.LSTM(...) object, store it,
        and return its UUID for tracking.
        """
        # We’ll pass these as arguments to a new “context=nn_module, method=create_lstm_module.”
        # The server side will interpret these, create LSTM, store it, return {uuid=...}.
        uuid = self.generic_call(
            "torch.nn", 
            "LSTM",
            input_size,
            hidden_size,
            num_layers,
            bias,
            batch_first,
            dropout,
            bidirectional,
            call_type="constructor"
        )
        # The server will return e.g. {"type": "module", "uuid": "..."} 
        return uuid
    
    def forward(self, module_uuid: str, input_tensor: Tensor, hx=None):
        """
        This calls the existing server reflection to do module.forward(input_tensor, hx).
        The server now returns a nested list: [ (out_uuid, out_shape, out_dtype),
                                              [ (h_uuid, h_shape, h_dtype),
                                                (c_uuid, c_shape, c_dtype) ] ]
        We'll parse it accordingly.
        """
        args = [module_uuid, input_tensor.uuid]
        if hx is not None:
            # hx = (h0, c0)
            h_uuid = hx[0].uuid
            c_uuid = hx[1].uuid
            args.extend([h_uuid, c_uuid])

        # generic_call returns a dict describing output, h_n, c_n, etc.
        # Something like:
        # {
        #   "output": ["uuid_for_output", [shape], "torch.float32"],
        #   "h_n":    ["uuid_for_hn",     [shape], "torch.float32"],
        #   "c_n":    ["uuid_for_cn",     [shape], "torch.float32"]
        # }
        raw_result = self.generic_call("torch.nn", "forward", *args, call_type="forward")


        # raw_result is presumably a list of length 2:
        # [
        #   (out_uuid, out_shape, out_dtype),
        #   [
        #     (h_uuid, h_shape, h_dtype),
        #     (c_uuid, c_shape, c_dtype)
        #   ]
        # ]
        # We'll parse it carefully:
        out_info, hc_info = raw_result
        # out_info = (out_uuid, out_shape, out_dtype)
        (out_uuid, out_shape, out_dtype) = out_info

        # hc_info is a list: [ (h_uuid,h_shape,h_dtype), (c_uuid,c_shape,c_dtype) ]
        h_info, c_info = hc_info
        (h_uuid, h_shape, h_dtype) = h_info
        (c_uuid, c_shape, c_dtype) = c_info

        # Now we can build MyTorch Tensor objects
        from torch.Tensor import Tensor  # local import to avoid circular references
        out_tensor = Tensor(out_uuid, out_shape, out_dtype)
        h_n = Tensor(h_uuid, h_shape, h_dtype)
        c_n = Tensor(c_uuid, c_shape, c_dtype)

        return (out_tensor, (h_n, c_n))
