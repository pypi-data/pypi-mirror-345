from proxies.mytorch.nn.module_proxy import ModuleProxy
from torch.cqbase import CQBase
    
class  Module(CQBase):
    def __init__(self, uuid=None):
        CQBase.__init__(self)
        self.proxy = ModuleProxy()
        if uuid is None:
            uuid = self.proxy.create_module_on_server()
        self.set_uuid(uuid)

    def set_uuid(self, uuid):
        self.uuid = uuid
        self.proxy.uuid = uuid

    
    # It is probably possible to make a generic fix for the _in_super_call logic.
    # Also this hasn't been tested for sub-sub-classes of Module / Sequential...
    def forward(self, input_data):
        # Save the original value of _in_super_call
        original_in_super_call = getattr(self.local_data, '_in_super_call', False)
        # Set _in_super_call to True to indicate that the method is being called from a super() call
        self.local_data._in_super_call = True
        try:
            # Call the forward method on the server using the proxy
            return self.proxy.forward(input_data)
        finally:
            # Restore the original value of _in_super_call
            self.local_data._in_super_call = original_in_super_call

    def __call__(self, input_data):
        return self.forward(input_data)

    def state_dict(self) -> dict:
        return self.proxy.state_dict()

    def load_state_dict(self, dict):
        return self.proxy.load_state_dict(dict)

    def eval(self):
        self.proxy.eval()

    def to(self, device):
        self.proxy.to_device(device)

    def parameters(self):
        return self.proxy.parameters()

    def half(self):
        return self.proxy.half()

    def cuda(self):
        return self.proxy.to_device("cuda")

    def cpu(self):
        return self.proxy.to_device("cpu")
    
    def train(self, mode=True):
        self.proxy.train(mode)
