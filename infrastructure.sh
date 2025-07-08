#!/bin/bash

echo "---- Infrastructure Setup Script ----"

# Update package list
sudo apt-get update -y

# ----------------------
# Install Docker
# ----------------------
echo "Installing Docker..."
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) \
  signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Enable Docker service
sudo systemctl enable docker
sudo systemctl start docker
echo "Docker installed and started."

# ----------------------
# Install Prometheus Node Exporter
# ----------------------
echo "Installing Prometheus Node Exporter..."
NODE_EXPORTER_VERSION="1.8.1"
curl -LO https://github.com/prometheus/node_exporter/releases/download/v$NODE_EXPORTER_VERSION/node_exporter-$NODE_EXPORTER_VERSION.linux-amd64.tar.gz
tar xvf node_exporter-$NODE_EXPORTER_VERSION.linux-amd64.tar.gz
sudo cp node_exporter-$NODE_EXPORTER_VERSION.linux-amd64/node_exporter /usr/local/bin/
sudo useradd -rs /bin/false node_exporter
sudo tee /etc/systemd/system/node_exporter.service > /dev/null <<EOF
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=default.target
EOF

sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter
echo "Node Exporter installed and running."

# ----------------------
# Install Loki using Docker
# ----------------------
echo "Installing Loki..."
sudo docker pull grafana/loki:latest
sudo docker run -d --name=loki \
  -p 3100:3100 \
  -v /etc/loki:/etc/loki \
  grafana/loki:latest \
  -config.file=/etc/loki/local-config.yaml
echo "Loki running on port 3100."

# ----------------------
# Install Python and pip dependencies
# ----------------------
echo "Installing Python3 and pip..."
sudo apt-get install -y python3 python3-pip

echo "Installing Python packages..."
pip3 install requests psutil

echo "---- Setup Complete ----"
