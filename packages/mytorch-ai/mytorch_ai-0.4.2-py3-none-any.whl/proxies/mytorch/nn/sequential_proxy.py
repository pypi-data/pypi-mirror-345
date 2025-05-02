###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from gRPC_impl.mytorch.nn import sequential_pb2_grpc, nn_msg_types_pb2
from utils.logger import Logger
from proxies.mytorch.nn.module_proxy import ModuleProxy
from connection_utils.server_connection import wrap_with_error_handler

class SequentialProxy(ModuleProxy):
    def __init__(self, *layers):
        super().__init__()  # Initializes Module, which sets up the module_stub and channel
        self.sequential_stub = sequential_pb2_grpc.SequentialServiceStub(self.channel)
        self.logger = Logger.get_logger()
        self.layers = layers
        self.uuid = None

    @wrap_with_error_handler
    def create_sequential_on_server(self):
        layer_descriptions = '\n...'.join([layer.describe() for layer in self.layers])
        self.logger.info(f"Creating Sequential model with layers:\n...{layer_descriptions}")

        # Assuming `layers` is a list of LayerProxy objects or its subclasses (LinearProxy, ReLUProxy, etc.)
        serialized_layers = []

        for layer in self.layers:
            # Create an NNLayer message for each layer
            nn_layer_msg = nn_msg_types_pb2.NNLayer()
            nn_layer_msg.type = layer.layer_type.name
            # Assuming params is a list of strings for simplicity. Adjust based on actual structure.
            # If params need to be key-value pairs serialized as strings, you'll need additional logic to format them.
            for key, value in layer.params.items():
                nn_layer_msg.params.append(f"{key}={value}")

            serialized_layers.append(nn_layer_msg)

        # Create the NNLayers message
        nn_layers_msg = nn_msg_types_pb2.NNLayers()
        nn_layers_msg.layers.extend(serialized_layers)  # Add the NNLayer messages to the NNLayers message

        response = self.sequential_stub.CreateSequentialModuleOnServer(nn_layers_msg)
        self.uuid = response.uuid
        return response.uuid
