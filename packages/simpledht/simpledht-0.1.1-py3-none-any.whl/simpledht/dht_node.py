import socket
import threading
import json
import hashlib
from typing import Dict, Optional, Tuple
import requests
from datetime import datetime
import netifaces

class DHTNode:
    def __init__(self, host: str, port: int, bootstrap_nodes: list = None):
        self.host = host
        self.port = port
        self.id = self._generate_node_id(host, port)
        self.data: Dict[str, str] = {}
        self.routing_table: Dict[str, Tuple[str, int]] = {}
        self.bootstrap_nodes = bootstrap_nodes or []
        self.running = False
        
        # Create socket with proper options for cross-network communication
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # Bind to all interfaces if host is 0.0.0.0
        if host == '0.0.0.0':
            self.socket.bind(('0.0.0.0', port))
            # Get actual IP address
            self.public_ip = self._get_public_ip()
            self.local_ips = self._get_local_ips()
        else:
            self.socket.bind((host, port))
            self.public_ip = host
            self.local_ips = [host]
        
        # Add self to routing table
        self.routing_table[self.id] = (self.public_ip, port)
        print(f"Node initialized with public IP: {self.public_ip}")

    def _get_public_ip(self) -> str:
        """Get the public IP address of this node."""
        try:
            response = requests.get('https://api.ipify.org?format=json', timeout=5)
            return response.json()['ip']
        except Exception as e:
            print(f"Failed to get public IP: {e}")
            return '0.0.0.0'

    def _get_local_ips(self) -> list:
        """Get all local IP addresses of this node."""
        ips = []
        for interface in netifaces.interfaces():
            try:
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        if 'addr' in addr:
                            ips.append(addr['addr'])
            except Exception as e:
                print(f"Failed to get IP for interface {interface}: {e}")
        return ips

    def _generate_node_id(self, host: str, port: int) -> str:
        """Generate a unique node ID based on host and port."""
        return hashlib.sha256(f"{host}:{port}".encode()).hexdigest()[:16]

    def start(self):
        """Start the DHT node."""
        self.running = True
        print(f"Starting DHT node {self.id} on {self.public_ip}:{self.port}")
        print(f"Local IPs: {', '.join(self.local_ips)}")
        
        # Start listening for messages
        listen_thread = threading.Thread(target=self._listen)
        listen_thread.start()

        # Bootstrap with other nodes if available
        if self.bootstrap_nodes:
            self._bootstrap()

    def _listen(self):
        """Listen for incoming messages."""
        while self.running:
            try:
                data, addr = self.socket.recvfrom(4096)
                message = json.loads(data.decode())
                self._handle_message(message, addr)
            except Exception as e:
                print(f"Error handling message: {e}")

    def _handle_message(self, message: dict, addr: Tuple[str, int]):
        """Handle incoming messages."""
        msg_type = message.get('type')
        
        if msg_type == 'ping':
            self._send_response(addr, {'type': 'pong'})
        elif msg_type == 'store':
            key = message.get('key')
            value = message.get('value')
            if key and value:
                self.data[key] = value
                # Replicate to other nodes
                self._replicate_data(key, value)
                self._send_response(addr, {'type': 'store_ack'})
        elif msg_type == 'get':
            key = message.get('key')
            if key in self.data:
                self._send_response(addr, {
                    'type': 'get_response',
                    'value': self.data[key]
                })
            else:
                # If not found locally, check other nodes
                self._forward_get_request(key, addr)
        elif msg_type == 'join':
            # Add the joining node to our routing table
            node_id = message.get('node_id')
            host = message.get('host')
            port = message.get('port')
            if node_id and host and port:
                self.routing_table[node_id] = (host, port)
                # Send our routing table to the new node
                self._send_response(addr, {
                    'type': 'join_ack',
                    'routing_table': self.routing_table
                })
        elif msg_type == 'join_ack':
            # Update our routing table with the received nodes
            received_table = message.get('routing_table', {})
            self.routing_table.update(received_table)

    def _replicate_data(self, key: str, value: str):
        """Replicate data to other nodes in the network."""
        for node_id, (host, port) in self.routing_table.items():
            if node_id != self.id:  # Don't send to self
                try:
                    self._send_message((host, port), {
                        'type': 'store',
                        'key': key,
                        'value': value
                    })
                except Exception as e:
                    print(f"Failed to replicate to {host}:{port}: {e}")

    def _forward_get_request(self, key: str, original_addr: Tuple[str, int]):
        """Forward a get request to other nodes if not found locally."""
        for node_id, (host, port) in self.routing_table.items():
            if node_id != self.id:  # Don't send to self
                try:
                    response = self._send_message_with_response((host, port), {
                        'type': 'get',
                        'key': key
                    })
                    if response.get('type') == 'get_response' and response.get('value') is not None:
                        # Forward the response back to the original requester
                        self._send_message(original_addr, response)
                        return
                except Exception as e:
                    print(f"Failed to forward get request to {host}:{port}: {e}")
        
        # If no node had the value, send a negative response
        self._send_message(original_addr, {
            'type': 'get_response',
            'value': None
        })

    def _send_message_with_response(self, addr: Tuple[str, int], message: dict) -> dict:
        """Send a message and wait for response."""
        self._send_message(addr, message)
        data, _ = self.socket.recvfrom(4096)
        return json.loads(data.decode())

    def _send_response(self, addr: Tuple[str, int], response: dict):
        """Send a response to a node."""
        self.socket.sendto(json.dumps(response).encode(), addr)

    def _bootstrap(self):
        """Connect to bootstrap nodes."""
        for node in self.bootstrap_nodes:
            try:
                # Split the address and handle potential errors
                parts = node.split(':')
                if len(parts) != 2:
                    print(f"Invalid bootstrap node format: {node}. Expected format: IP:PORT")
                    continue
                
                host, port = parts
                try:
                    port = int(port)
                except ValueError:
                    print(f"Invalid port number in bootstrap node: {node}")
                    continue
                
                print(f"Attempting to bootstrap with node {host}:{port}")
                self._send_message((host, port), {
                    'type': 'join',
                    'node_id': self.id,
                    'host': self.public_ip,
                    'port': self.port
                })
            except Exception as e:
                print(f"Failed to bootstrap with {node}: {e}")

    def _send_message(self, addr: Tuple[str, int], message: dict):
        """Send a message to another node."""
        self.socket.sendto(json.dumps(message).encode(), addr)

    def stop(self):
        """Stop the DHT node."""
        self.running = False
        self.socket.close() 