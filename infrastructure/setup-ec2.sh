#!/bin/bash
# EC2 Instance Setup Script for MLOps Pipeline

set +e

echo "🔧 Setting up EC2 instance for MLOps deployment..."

# Update system
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker ubuntu
sudo systemctl enable docker
sudo systemctl start docker

# Install AWS CLI v2
echo "☁️ Installing AWS CLI..."
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo apt-get install -y unzip
unzip awscliv2.zip
sudo ./aws/install
rm -rf awscliv2.zip aws/

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Python and pip
echo "🐍 Installing Python..."
sudo apt-get install -y python3 python3-pip python3-venv
sudo ln -sf /usr/bin/python3 /usr/bin/python

# Install DVC
echo "📦 Installing DVC..."
pip3 install dvc[s3] --user

# Install monitoring tools
echo "📊 Installing monitoring tools..."
sudo apt-get install -y htop nginx

# Create application directory
sudo mkdir -p /opt/mlops-app
sudo chown ubuntu:ubuntu /opt/mlops-app

# Create systemd service for the ML API
sudo tee /etc/systemd/system/water-quality-api.service > /dev/null << EOF
[Unit]
Description=Water Quality API
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/bash -c 'docker stop water-quality-api || true; docker rm water-quality-api || true; docker run -d --name water-quality-api -p 8000:8000 --restart unless-stopped water-quality-api:latest'
ExecStop=docker stop water-quality-api
User=ubuntu
Group=ubuntu

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx as reverse proxy
sudo tee /etc/nginx/sites-available/mlops-app > /dev/null << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/mlops-app /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx

# Create log directories
sudo mkdir -p /var/log/mlops-app
sudo chown ubuntu:ubuntu /var/log/mlops-app

# Install CloudWatch agent (optional but recommended for production)
echo "📊 Installing CloudWatch agent..."
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb
rm amazon-cloudwatch-agent.deb

# Create CloudWatch config
sudo tee /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json > /dev/null << EOF
{
    "agent": {
        "metrics_collection_interval": 60
    },
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/mlops-app/*.log",
                        "log_group_name": "/aws/ec2/mlops-app",
                        "log_stream_name": "{instance_id}"
                    }
                ]
            }
        }
    },
    "metrics": {
        "namespace": "MLOps/App",
        "metrics_collected": {
            "cpu": {
                "measurement": [
                    "cpu_usage_idle",
                    "cpu_usage_iowait",
                    "cpu_usage_user",
                    "cpu_usage_system"
                ],
                "metrics_collection_interval": 60
            },
            "disk": {
                "measurement": [
                    "used_percent"
                ],
                "metrics_collection_interval": 60,
                "resources": [
                    "*"
                ]
            },
            "mem": {
                "measurement": [
                    "mem_used_percent"
                ],
                "metrics_collection_interval": 60
            }
        }
    }
}
EOF

# Enable and start services
sudo systemctl enable docker
sudo systemctl enable amazon-cloudwatch-agent

echo ""
echo "✅ EC2 instance setup complete!"
echo ""
echo "📋 Instance is configured with:"
echo "- Docker and Docker Compose"
echo "- AWS CLI v2"
echo "- DVC with S3 support"
echo "- Nginx reverse proxy"
echo "- CloudWatch agent"
echo "- Systemd service for the ML API"
echo ""
echo "🔧 Manual steps required:"
echo "1. Configure AWS credentials: aws configure"
echo "2. Test Docker access: docker run hello-world"
echo "3. Start CloudWatch agent: sudo systemctl start amazon-cloudwatch-agent"
echo ""
echo "🚀 Ready for deployment!"