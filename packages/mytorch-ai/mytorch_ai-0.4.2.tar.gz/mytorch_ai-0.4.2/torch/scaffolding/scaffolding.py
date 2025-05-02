###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

from utils.MyTorchClient import MyTorchClient
from proxies.mytorch.scaffolding.scaffolding_proxy import ScaffoldingProxy
from connection_utils.server_resolver import ServerResolver
import datetime

SERVER_LOCALHOST = 'LOCALHOST'
SERVER_AWS = 'AWS'
SERVER_TITAN = 'TITAN'
SERVER_FUNC2 = 'func2'
SERVER_CACHEQ_AI = 'mytorch.scaffolding.ai'
SERVER_NEURON = 'neuron'

def print_timing_data(summary_only: bool = False):
    MyTorchClient.instance().print_timing_data(summary_only)
    
def get_timing_data():
    return MyTorchClient.instance().get_timing_data()

### TO DO - for timing data: 
### Assume 1 current_run per client, many conections per server
### End_run should set current_run to None, deal with it.
### Also on the server, scaffolding_server_get_timing_statistics, delete data for run.
### Assume data only fetched once at end_run (so clean up memory).
### Also it would be good to delete old timing data if never fetched.
### Check for these assumptions and warn if not met.
### Client TimingData keeps data for many runs, for later graphing.
### The run_id name could encode more in engish string, cpu or gpu for example.
### Could also hold codes for different GPU types "AWS GPU_M100" for example.
### IF begin or end run methods not called, it's ok, this is optional timing data.
### Check / test these edge conditions. 

def begin_run(run_id=None):
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    if run_id is None:    
        run_id = current_time
    else:
        run_id += "::" + current_time
    MyTorchProxy().scaffolding_server_initialize_timing_statistics(run_id)
    MyTorchClient.instance().begin_run(run_id)
    return run_id

def end_run(run_id=None):
    if run_id is None:
        run_id = MyTorchClient.instance().get_current_run_id()
    stats_json = MyTorchProxy().scaffolding_server_get_timing_statistics(run_id)
    MyTorchClient.instance().end_run(run_id, stats_json)

def select_server(server, port=50051) -> tuple[str, str, int]: # server_name, server_ip, server_port
    server_info = MyTorchClient.instance().select_server(server, port)
    client_info = MyTorchClient.instance().get_client_info()
    ScaffoldingProxy().initialize_client_connection(client_info)
    return server_info

def select_server_by_ip(ip, port=50051):
    server_info = MyTorchClient.instance().select_server_by_ip(ip, port)
    client_info = MyTorchClient.instance().get_client_info()
    ScaffoldingProxy().initialize_client_connection(client_info)
    return server_info

def select_server_by_env_var():
    server_info = MyTorchClient.instance().select_server_by_env_var()
    client_info = MyTorchClient.instance().get_client_info()
    ScaffoldingProxy().register_client_with_server(client_info)

def get_server_name():
    return MyTorchClient.instance().get_server_name()

def get_server():
    return MyTorchClient.instance().get_server()

def connect_via(dns_name) -> tuple[str, str, int]: # server_name, server_port, server_ip
    server_resolver = ServerResolver(dns_name)
    return server_resolver.connect_to_server()

### CACHEQ server-side methods:

def scaffolding_server_get_timing_statistics(run_id):
    stats_json = MyTorchProxy().scaffolding_server_get_timing_statistics(run_id)
    MyTorchClient.instance().set_server_timing_statistics(stats_json)
    return stats_json

def scaffolding_server_initialize_timing_statistics(run_id):
    MyTorchProxy().scaffolding_server_initialize_timing_statistics(run_id)

def set_overwrite_server_data(overwrite: bool):
    MyTorchClient.instance().set_overwrite_server_data(overwrite)

def get_gpu_info():
    return MyTorchProxy().get_gpu_info()


    