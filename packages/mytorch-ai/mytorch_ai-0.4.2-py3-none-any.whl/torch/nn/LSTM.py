###############################################################################
# File: mytorch/client/torch/nn/LSTM.py
###############################################################################
from torch.nn.Module import Module
from proxies.mytorch.nn.lstm_proxy import LSTMProxy
from torch.Tensor import Tensor

class LSTM(Module):
    """
    An LSTM Module that registers a server-side LSTM object and delegates
    forward calls to it. We can call forward(input, hx) multiple times
    with persistent server-side weights.
    """

    def __init__(self, input_size, hidden_size, num_layers=1, bias=True, batch_first=False,
                 dropout=0.0, bidirectional=False):
        # We call super().__init__() so a new server-side “Module” UUID can be tracked.
        super().__init__(uuid=None)  
        
        # Create our specialized LSTM proxy
        self.proxy = LSTMProxy()

        # Instruct the server to create a brand new torch.nn.LSTM(...) object
        new_uuid = self.proxy.create_lstm_on_server(
            input_size, hidden_size, num_layers, bias, batch_first, dropout, bidirectional
        )

        # Our parent Module class expects us to set self.uuid to the server’s object
        self.set_uuid(new_uuid)

    def forward(self, input: Tensor, hx=None):
        """
        In real PyTorch, LSTM returns (output, (h_n, c_n)).
        We'll do the same by delegating to LSTMProxy.forward(...).
        """
        return self.proxy.forward(self.uuid, input, hx)

