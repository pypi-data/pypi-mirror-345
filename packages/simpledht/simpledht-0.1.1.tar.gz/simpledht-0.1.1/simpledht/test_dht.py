import subprocess
import time
import click
from dht_node import DHTNode
import socket
import json

def start_node(host, port, bootstrap=None):
    """Start a DHT node in a separate process."""
    cmd = ['python', 'cli.py', 'start', '--host', host, '--port', str(port)]
    if bootstrap:
        cmd.extend(['--bootstrap', bootstrap])
    return subprocess.Popen(cmd)

def send_message(host, port, message):
    """Send a message to a DHT node."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(json.dumps(message).encode(), (host, port))
        sock.settimeout(5.0)
        data, _ = sock.recvfrom(4096)
        return json.loads(data.decode())
    finally:
        sock.close()

@click.command()
def test():
    """Test the DHT with multiple nodes."""
    click.echo("Starting DHT test with 2 nodes...")
    
    # Start first node
    click.echo("\nStarting Node 1 (0.0.0.0:5000)...")
    node1 = start_node('0.0.0.0', 5000)
    time.sleep(2)  # Wait for node to start
    
    # Start second node and connect to first
    click.echo("Starting Node 2 (0.0.0.0:5001) and connecting to Node 1...")
    node2 = start_node('0.0.0.0', 5001, '0.0.0.0:5000')
    time.sleep(2)  # Wait for nodes to connect
    
    try:
        # Store data on Node 1
        click.echo("\nStoring data on Node 1...")
        response = send_message('0.0.0.0', 5000, {
            'type': 'store',
            'key': 'test_key',
            'value': 'test_value'
        })
        if response.get('type') == 'store_ack':
            click.echo("Successfully stored data on Node 1")
        
        # Retrieve data from Node 2
        click.echo("\nRetrieving data from Node 2...")
        response = send_message('0.0.0.0', 5001, {
            'type': 'get',
            'key': 'test_key'
        })
        if response.get('type') == 'get_response':
            value = response.get('value')
            if value:
                click.echo(f"Successfully retrieved value: {value}")
            else:
                click.echo("Failed to retrieve value")
        
        click.echo("\nTest completed!")
        
    finally:
        # Clean up
        click.echo("\nStopping nodes...")
        node1.terminate()
        node2.terminate()
        node1.wait()
        node2.wait()

if __name__ == '__main__':
    test() 