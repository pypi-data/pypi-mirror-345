import click
from dht_node import DHTNode
import json
import time
import socket
import sys

@click.group()
def cli():
    """Simple DHT CLI interface."""
    pass

@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=5000, help='Port to bind to')
@click.option('--bootstrap', help='Comma-separated list of bootstrap nodes (host:port)')
def start(host, port, bootstrap):
    """Start a new DHT node."""
    bootstrap_nodes = bootstrap.split(',') if bootstrap else []
    node = DHTNode(host, port, bootstrap_nodes)
    node.start()
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        node.stop()

def _send_message(host: str, port: int, message: dict, timeout: int = 5) -> dict:
    """Send a message to a DHT node and wait for response."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Set timeout before sending
        sock.settimeout(timeout)
        
        # Send message
        click.echo(f"Sending message to {host}:{port}...")
        sock.sendto(json.dumps(message).encode(), (host, port))
        
        # Wait for response
        try:
            data, _ = sock.recvfrom(4096)
            return json.loads(data.decode())
        except socket.timeout:
            click.echo(f"Error: No response received from {host}:{port} within {timeout} seconds")
            click.echo("Possible reasons:")
            click.echo("1. The node is not running")
            click.echo("2. The port is blocked by a firewall")
            click.echo("3. The node is behind NAT without port forwarding")
            sys.exit(1)
    except Exception as e:
        click.echo(f"Error sending message: {e}")
        sys.exit(1)
    finally:
        sock.close()

@cli.command()
@click.option('--host', required=True, help='Host of the DHT node')
@click.option('--port', required=True, type=int, help='Port of the DHT node')
@click.option('--timeout', default=5, help='Timeout in seconds')
@click.argument('key')
@click.argument('value')
def put(host, port, timeout, key, value):
    """Store a key-value pair in the DHT."""
    response = _send_message(host, port, {
        'type': 'store',
        'key': key,
        'value': value
    }, timeout)
    
    if response.get('type') == 'store_ack':
        click.echo(f"Successfully stored {key}={value}")
    else:
        click.echo(f"Failed to store {key}={value}")

@cli.command()
@click.option('--host', required=True, help='Host of the DHT node')
@click.option('--port', required=True, type=int, help='Port of the DHT node')
@click.option('--timeout', default=5, help='Timeout in seconds')
@click.argument('key')
def get(host, port, timeout, key):
    """Retrieve a value from the DHT."""
    response = _send_message(host, port, {
        'type': 'get',
        'key': key
    }, timeout)
    
    if response.get('type') == 'get_response':
        value = response.get('value')
        if value is None:
            click.echo(f"No value found for key: {key}")
        else:
            click.echo(f"Value for {key}: {value}")
    else:
        click.echo(f"Failed to retrieve value for key: {key}")

if __name__ == '__main__':
    cli() 