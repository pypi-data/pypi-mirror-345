"""
SimpleDHT - A simple distributed hash table implementation
"""

__version__ = "0.1.0"

from .dht_node import DHTNode
from .cli import main

__all__ = ["DHTNode", "main"] 