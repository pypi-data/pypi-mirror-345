###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

import socket
import random
import requests
from utils.logger import Logger
from connection_utils.resource_mgr_connection import ResourceMgrConnection
import torch.scaffolding as scaffolding

IP_LOOKUP_SERVICE = 'https://api.ipify.org'

class ServerResolver:

    def __init__(self, dns_name: str):
        self.dns_name = dns_name
        self.logger = Logger.get_logger()
        self.resource_mgr_ip = None
        self.client_ip = None


    '''
    This gets the destination server for MyTorch to call. It uses a DNS name
    as an input to talk to the Resource Manager server. The Resource Manager server
    will return the server that the client should talk to.
    
    There are 3 steps involved
    1. Resolve the DNS name of the Resource Manager to an IP address
    2. Get the public-facing IP of this machine
    3. Call the Resource Manager to get the server to talk to
    '''
    def connect_to_server(self) -> tuple[str, str, int] | None: # (server_name, server_ip, server_port)
        # Resolve the DNS name of the Resource Manager to an IP address and connect to it
        self.resource_mgr_ip = self.get_resource_mgr_ip()
        self.logger.info(f"Resource Manager IP address: {self.resource_mgr_ip}")
        resource_mgr_conn = ResourceMgrConnection(self.resource_mgr_ip)

        # Get the public-facing IP of this machine
        self.client_ip = self.get_public_ip()
        self.logger.info(f"Client public-facing IP address: {self.client_ip}")

        # Call the Resource Manager to get the server to talk to
        resource_info_dict = resource_mgr_conn.get_destination_server_for_client(self.client_ip)
        destination_server_name = resource_info_dict['resource_name']
        destination_server_ip = resource_info_dict['resource_ip']
        destination_server_port = resource_info_dict['resource_port']
        self.logger.info(f"Destination server: {destination_server_name} at {destination_server_ip}:{destination_server_port}")

        # connect to the destination server
        return scaffolding.select_server_by_ip(destination_server_name, destination_server_ip, destination_server_port)

    '''
    This function returns the IP address of the resource manager server
    Since the resource manager server is a DNS name, we need to resolve it to an IP address. This
    resolution will return a list of IP addresses, but we only need one. We will return a random
    IP address from the list.
    '''
    def get_resource_mgr_ip(self) -> str | None:
        try:
            # Get all IP addresses for the given DNS name
            ip_addresses = socket.getaddrinfo(self.dns_name, None)
            # Filter out only IPv4 addresses
            ipv4_addresses = [ip[4][0] for ip in ip_addresses if ip[0] == socket.AF_INET]
            # Return a random IP address from the list
            return random.choice(ipv4_addresses)
        except socket.gaierror:
            raise Exception("Could not resolve the IP address of the Resource Manager server")

    def get_public_ip(self) -> str:
        """
        Fetches the public IP address of the system.
        Returns the public IP address as a string.
        """
        try:
            # Request the public IP from a third-party service
            ip_request = requests.get(IP_LOOKUP_SERVICE)
            # Check if the request was successful
            ip_request.raise_for_status()
            # Get the public IP address from the response
            public_ip = ip_request.text
            return public_ip
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching public IP of this machine: {e}")