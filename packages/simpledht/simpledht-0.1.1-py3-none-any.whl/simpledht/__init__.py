"""
SimpleDHT - A simple distributed hash table implementation

Example usage:
    from simpledht import DHTNode

    # Create a new node
    node = DHTNode(host='0.0.0.0', port=5000)
    
    # Start the node
    node.start()
    
    # Store a value
    node.put('mykey', 'myvalue')
    
    # Retrieve a value
    value = node.get('mykey')
    
    # Connect to another node
    node.bootstrap('other_node_ip:5000')
"""

__version__ = "0.1.1"

from .dht_node import DHTNode
from .cli import main as cli_main

__all__ = ["DHTNode", "cli_main"] 