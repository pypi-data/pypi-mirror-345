###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################
# Global "singleton" class, for client

import time
from utils.timing_data import TimingData
import uuid
import os
from utils.logger import Logger
import socket
import platform
import requests
import torch
import json

def generate_uuid() -> str:
    return uuid.uuid4().hex # convert UUID to a 32-character string


def get_client_info():
    # Get the hostname
    hostname = socket.gethostname()

    # Get the OS details
    os_name = platform.system()
    os_details = platform.platform()

    # Get the machine type
    machine = platform.machine()
    processor = platform.processor()
    hf_token = os.getenv('HF_TOKEN')
    if hf_token is None:
        # Obsolete usage
        hf_token = os.getenv('HUGGINGFACE_TOKEN')
    if hf_token is None:
        # try to load the token from the .env file in the user's home directory
        hf_token_path = os.path.join(os.path.expanduser('~'), '.cache/huggingface/token')
        if os.path.exists(hf_token_path):
            with open(hf_token_path, 'r') as f:
                hf_token = f.read().strip()
    if hf_token is not None:
        os.environ['HF_TOKEN'] = hf_token
        
    client_info = {
        'hostname': hostname,
        'env': json.dumps(dict(os.environ)),
        'os_name': os_name,
        'os_details': os_details,
        'machine': machine,
        'processor': processor,
        'mytorch_version': torch.__version__,
        'token': os.getenv('MYTORCH_TOKEN'),
    }

    return client_info

class MyTorchClient:
    
    _instance = None
    _current_run = "DEFAULT NAME" 
    _server_ip = 'localhost' # default
    _server_name = 'LOCALHOST' #default
    _server_port = 50051 # default
    _server_addresses = {
        "LOCALHOST": "localhost",
        "TITAN": "10.8.2.17",  # Must be using MyTorch VPN
        }
    _timing_data = TimingData()
    _overwrite_server_data = False
        
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MyTorchClient, cls).__new__(cls)
            cls._instance._client_id = generate_uuid()
            cls._instance._client_info = get_client_info()
        return cls._instance

    @classmethod
    def instance(cls):
        return cls()
    
    def select_server(self, server_name, server_port=50051) -> tuple[str, str, int] | None: # (server_name, server_ip, server_port)
        server_ip = self._server_addresses[server_name.upper()]
        self._server_ip = server_ip  # self._server_addresses[server_name.upper()]
        self._server_port = server_port
        self._server_name = server_name
        return self._server_name, self._server_ip, self._server_port

    def select_server_by_ip(self, server_ip, server_port=50051):
        # Check if server_ip contains a port specification
        if ':' in server_ip:
            ip_parts = server_ip.split(':')
            server_ip = ip_parts[0]
            server_port = int(ip_parts[1])
        self._server_ip = server_ip  
        self._server_port = server_port
        self._server_name = "N/A"
        return self._server_name, self._server_ip, self._server_port
    
    def select_server_by_proxy(self):
        """Fetches server details from the proxy service."""
        try:
            token = os.getenv('MYTORCH_TOKEN')
            if (token is None or token == ""):
                print("You must add your token to ~/.mytorch or set the MYTORCH_TOKEN environment variable.")
                exit(1)
            response = requests.get(f'https://proxy.mytorch.net/server_request?KEY={token}')

            response.raise_for_status()  # Raises an HTTPError for bad responses
            data = response.json()
            
            self._server_ip = data["SERVER"]
            self._server_port = int(data["PORT"])
            self._server_name = "PROXY"
            if self._server_port == 0: 
                Logger.get_logger().error("All mytorch servers are currently busy. Please try again later.")
                exit(1)
            return self._server_ip, self._server_port
        except Exception as e:
            Logger.get_logger().error(f"Failed to fetch server details from proxy: {str(e)}")
            return None
        
    def select_server_by_env_var(self):
        if not os.getenv('MYTORCH_SERVER_IP'):
            Logger.get_logger().error("MYTORCH_SERVER_IP environment variable not set")
            exit(1)
        server_ip = os.getenv('MYTORCH_SERVER_IP')
        server_port = 50051
        
        # Check if server_ip contains a port specification
        if ':' in server_ip:
            ip_parts = server_ip.split(':')
            server_ip = ip_parts[0]
            server_port = int(ip_parts[1])
        # Use environment port variable if provided and no port in IP
        elif os.getenv('MYTORCH_SERVER_PORT'):
            server_port = int(os.getenv('MYTORCH_SERVER_PORT'))
            
        self._server_ip = server_ip
        self._server_port = server_port
        return self._server_ip, self._server_port

    def get_server(self):
        return self._server_ip, self._server_port

    def get_server_name(self):
        return self._server_name, self._server_port

    def add_method_duration(self, method_name, duration):
        self._timing_data.add_method_duration(self._current_run, method_name, duration)

    def begin_run(self, run_id):
        self._current_run = run_id
        #self._timing_data.clear_statistics()
        start_time = time.perf_counter()
        self._timing_data.start_time(start_time, run_id)

    def end_run(self, run_id, server_stats_json):
        end_time = time.perf_counter()
        self._timing_data.end_time(end_time, run_id)
        server_data = TimingData()  # Temporary instance 
        server_data.init_from_json(server_stats_json, run_id)
        self._timing_data.incorporate_end_of_run_server_data(server_data, self._current_run)

    def get_current_run_id(self):
        return self._current_run
    
    def print_timing_data(self, summary_only=False):
        self._timing_data.print_statistics(summary_only)

    def get_timing_data(self):
        return self._timing_data.get_statistics(self._current_run)

    def clear_timing_data(self, run_id=None):
        self._timing_data.clear_statistics(run_id)

    def set_overwrite_server_data(self, overwrite: bool):
        self._overwrite_server_data = overwrite

    def get_overwrite_server_data(self):
        return self._overwrite_server_data

    def get_client_id(self):
        return self._client_id

    def get_client_info(self):
        return self._client_info
