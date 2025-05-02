# Abstract base class for proxy objects, to implement the generic_call approach.
import json
import numpy as np

from connection_utils.server_connection import wrap_with_error_handler
from gRPC_impl import shared_msg_types_pb2
from utils.logger import Logger
from gRPC_impl.mytorch import mytorch_pb2_grpc
from typing import Optional

class BaseProxy():
    def __init__(self):
        self.logger = Logger.get_logger()

    # GENERIC_CALL
    # Every call to generic_call(...) includes:
    # A standardized context (e.g., "torch", "torch.nn", "torch.Tensor")
    # An explicit and correct call_type (constructor, method, forward, function)
    @wrap_with_error_handler
    def generic_call(self, context: str, method: str, *args, call_type: str = "function", kwargs: Optional[dict] = None):
        """Handles a generic JSON request and returns a dynamic response."""
        print(f"Sending generic command: {context}: {method} {call_type} with args {args}, kwargs {kwargs}")
        #traceback.print_stack()
  
        method_json = json.dumps({
            "context": context,
            "method": method,
            "call_type": call_type,
            "args": args,
            "kwargs": kwargs or {}  
        })
    
        # Create a gRPC request
        request = shared_msg_types_pb2.JsonRequest()
        request.json_payload = method_json

        stub = mytorch_pb2_grpc.MyTorchServiceStub(self.channel)

        response: shared_msg_types_pb2.JsonResponse = stub.generic_call(request)

        # Decode JSON response
        result = json.loads(response.json_payload)

        # result could be just a simple type like the boolean True
        if isinstance(result, dict) and "error" in result:
            raise RuntimeError(f"Server Error: {result['error']}")

        return self._deserialize_response(result)

    def _deserialize_response(self, response: dict):
        """Converts a top-level JSON dict into the final Python object."""
        return self._deserialize_anything(response)


    def _deserialize_anything(self, resp_data):
        """
        Recursively convert the JSON response structure back into a Python
        object (e.g., (uuid, shape, dtype) for Tensors, 
        or nested lists, or ...).
        """

        # If it's a list, parse each item
        if isinstance(resp_data, list):
            return [self._deserialize_anything(item) for item in resp_data]

        # If it's not a dict, just return it as-is (e.g. int, float, str, bool)
        if not isinstance(resp_data, dict):
            return resp_data

        # If it is a dict, see if there's a 'type' field
        if "type" not in resp_data:
            # It's just a normal dictionary with no "type" – recursively parse each value
            return {k: self._deserialize_anything(v) for k, v in resp_data.items()}

        # Now we have a dict that has 'type'
        resp_type = resp_data["type"]

        if resp_type == "tensor":
            return (resp_data["uuid"], resp_data["shape"], resp_data["dtype"])

        elif resp_type == "module":
            return resp_data["uuid"]

        elif resp_type == "optimizer":
            return resp_data["uuid"]
        
        elif resp_type == "dataset":
            return (resp_data["uuid"], resp_data["dataset_length"])

        elif resp_type == "dataloader":
            return (
                resp_data["uuid"],
                resp_data["dataset_length"],
                resp_data["batch_size"]
            )

        elif resp_type == "scalar":
            return resp_data["value"]

        elif resp_type == "bool":
            return bool(resp_data["value"])

        elif resp_type == "list":
            # e.g. {"type": "list","value":[...]}
            return [self._deserialize_anything(item) for item in resp_data["value"]]

        # If there's some known or unknown type, handle or fallback:
        # e.g. "unknown", "dict", or others
        elif resp_type == "unknown":
            return resp_data["value"]  # fallback
        elif resp_type == "dict":
            # e.g. {"type":"dict","value":{...}} if your server used that approach
            inner = resp_data.get("value", {})
            return {k: self._deserialize_anything(v) for k, v in inner.items()}

        else:
            raise ValueError(f"Unknown response type: {resp_type}")
