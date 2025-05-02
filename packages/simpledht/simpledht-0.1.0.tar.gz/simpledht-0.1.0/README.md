# Distributed Hash Table (DHT) Implementation

A Python-based Distributed Hash Table implementation that allows nodes to connect across different networks using IP addresses. This implementation supports key-value storage and retrieval across multiple nodes.

## Features

- Cross-network node communication
- Key-value storage and retrieval
- Automatic node discovery
- Data replication between nodes
- Simple CLI interface
- Public IP detection
- Local network support

## Installation

### From PyPI (Recommended)

```bash
pip install simpledht
```

### From Source

1. Clone the repository:
```bash
git clone <repository-url>
cd SimpleDHT
```

2. Create and activate a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install the package in development mode:
```bash
pip install -e .
```

## Usage

### Starting a Node

To start a new DHT node:
```bash
python cli.py start --host 0.0.0.0 --port 5000
```

To start a node and connect to existing nodes:
```bash
python cli.py start --host 0.0.0.0 --port 5001 --bootstrap "PUBLIC_IP:5000"
```

### Storing Data

To store a key-value pair:
```bash
python cli.py put --host PUBLIC_IP --port 5000 mykey "my value"
```

### Retrieving Data

To retrieve a value:
```bash
python cli.py get --host PUBLIC_IP --port 5000 mykey
```

### Cross-Network Example

1. Start Node 1 (First network):
```bash
python cli.py start --host 0.0.0.0 --port 5000
```

2. Start Node 2 (Second network):
```bash
python cli.py start --host 0.0.0.0 --port 5000 --bootstrap "NODE1_PUBLIC_IP:5000"
```

3. Store and retrieve data:
```bash
# Store on Node 1
python cli.py put --host NODE1_PUBLIC_IP --port 5000 test_key "test_value"

# Retrieve from Node 2
python cli.py get --host NODE2_PUBLIC_IP --port 5000 test_key
```

## Network Configuration

### Firewall Setup

Ensure the UDP port (default: 5000) is open in your firewall:

```bash
# For UFW (Ubuntu)
sudo ufw allow 5000/udp

# For iptables
sudo iptables -A INPUT -p udp --dport 5000 -j ACCEPT
```

### Port Forwarding

If your node is behind a NAT router:
1. Access your router's admin interface
2. Set up port forwarding for UDP port 5000
3. Forward to your node's local IP address

## Troubleshooting

### Common Issues

1. **Connection Timeout**
   - Check if the target node is running
   - Verify firewall settings
   - Ensure port forwarding is configured correctly
   - Try increasing the timeout: `--timeout 10`

2. **Address Already in Use**
   - The port is already being used by another process
   - Try a different port number
   - Check running processes: `netstat -tuln | grep 5000`

3. **No Response from Node**
   - Verify the node is running
   - Check network connectivity: `ping NODE_IP`
   - Test port connectivity: `nc -vzu NODE_IP 5000`

### Error Messages

- `Failed to bootstrap with IP:PORT`: Invalid bootstrap node format
- `No response received`: Node is not responding
- `Address already in use`: Port conflict
- `Failed to get public IP`: Network connectivity issue

## Architecture

The DHT implementation uses:
- UDP sockets for communication
- SHA-256 for node ID generation
- Automatic public IP detection
- Data replication between nodes
- Bootstrap nodes for network discovery

## Security Considerations

- This is a basic implementation and should not be used in production without additional security measures
- Consider adding:
  - Encryption for data in transit
  - Authentication for node joining
  - Rate limiting to prevent abuse
  - Input validation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
