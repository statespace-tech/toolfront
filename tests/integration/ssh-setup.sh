#!/bin/bash
# SSH server setup script for integration testing

# Create test user with password authentication
echo "bastionuser:bastionpass" | chpasswd

# Enable password authentication and port forwarding
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/#AllowTcpForwarding yes/AllowTcpForwarding yes/' /etc/ssh/sshd_config
sed -i 's/AllowTcpForwarding no/AllowTcpForwarding yes/' /etc/ssh/sshd_config
echo "AllowTcpForwarding yes" >> /etc/ssh/sshd_config
echo "GatewayPorts no" >> /etc/ssh/sshd_config

# Ensure SSH user can access postgres host
echo "Setting up SSH user environment..."

# Create .ssh directory if it doesn't exist
mkdir -p /home/bastionuser/.ssh
chown bastionuser:bastionuser /home/bastionuser/.ssh
chmod 700 /home/bastionuser/.ssh

# Install PostgreSQL client for testing connectivity from bastion
apk add --no-cache postgresql-client

echo "SSH setup completed successfully"