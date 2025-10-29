#!/bin/bash
# Blue-Green deployment script for zero-downtime production deployments

set -euo pipefail

IMAGE_URI=${1:-"latest"}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔄 Starting Blue-Green deployment"
echo "📦 New image: $IMAGE_URI"

# Configuration
BLUE_CONTAINER="mlops-app-blue"
GREEN_CONTAINER="mlops-app-green"
NGINX_CONFIG_DIR="/etc/nginx/sites-available"
CURRENT_UPSTREAM_FILE="/tmp/current_upstream"
HEALTH_CHECK_URL="http://localhost"

# Determine current active environment
if docker ps --format "table {{.Names}}" | grep -q $BLUE_CONTAINER; then
    CURRENT_ENV="blue"
    NEW_ENV="green"
    CURRENT_CONTAINER=$BLUE_CONTAINER
    NEW_CONTAINER=$GREEN_CONTAINER
    NEW_PORT=8001
else
    CURRENT_ENV="green"
    NEW_ENV="blue"
    CURRENT_CONTAINER=$GREEN_CONTAINER
    NEW_CONTAINER=$BLUE_CONTAINER
    NEW_PORT=8000
fi

echo "🔵🟢 Current environment: $CURRENT_ENV"
echo "🔵🟢 Deploying to: $NEW_ENV (port $NEW_PORT)"

# AWS ECR login
echo "🔐 Logging into AWS ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# Pull new image
echo "📥 Pulling new Docker image..."
docker pull $IMAGE_URI

# Stop and remove existing new environment container
docker stop $NEW_CONTAINER 2>/dev/null || true
docker rm $NEW_CONTAINER 2>/dev/null || true

# Start new container in new environment
echo "🚀 Starting new container in $NEW_ENV environment..."
docker run -d \
    --name $NEW_CONTAINER \
    --restart unless-stopped \
    -p $NEW_PORT:8000 \
    -e ENVIRONMENT=production \
    -e MLFLOW_TRACKING_URI="$MLFLOW_TRACKING_URI" \
    -e MLFLOW_TRACKING_USERNAME="$MLFLOW_TRACKING_USERNAME" \
    -e MLFLOW_TRACKING_PASSWORD="$MLFLOW_TRACKING_PASSWORD" \
    -e AWS_REGION="$AWS_REGION" \
    -v /opt/mlops-production/logs:/app/logs \
    -v /opt/mlops-production/data:/app/data \
    --log-driver=awslogs \
    --log-opt awslogs-group="/aws/ec2/mlops-production" \
    --log-opt awslogs-region="$AWS_REGION" \
    --log-opt awslogs-stream="\$(hostname)-$NEW_ENV" \
    $IMAGE_URI

# Health check new environment
echo "🏥 Health checking new environment..."
sleep 45

HEALTH_CHECK_PASSED=false
for i in {1..20}; do
    if curl -f $HEALTH_CHECK_URL:$NEW_PORT/health > /dev/null 2>&1; then
        echo "✅ Health check passed for $NEW_ENV environment!"
        HEALTH_CHECK_PASSED=true
        break
    else
        echo "⏳ Health check attempt $i failed, retrying..."
        sleep 15
    fi
done

if [ "$HEALTH_CHECK_PASSED" = false ]; then
    echo "❌ Health check failed for new environment"
    echo "📋 Container logs:"
    docker logs $NEW_CONTAINER
    
    # Cleanup failed deployment
    docker stop $NEW_CONTAINER
    docker rm $NEW_CONTAINER
    exit 1
fi

# Run smoke tests on new environment
echo "🧪 Running smoke tests on new environment..."
python3 $SCRIPT_DIR/../tests/smoke/test_production.py --base-url $HEALTH_CHECK_URL:$NEW_PORT || {
    echo "❌ Smoke tests failed"
    docker stop $NEW_CONTAINER
    docker rm $NEW_CONTAINER
    exit 1
}

# Update Nginx upstream to point to new environment
echo "🔀 Switching traffic to $NEW_ENV environment..."

# Backup current nginx config
cp $NGINX_CONFIG_DIR/mlops-app $NGINX_CONFIG_DIR/mlops-app.backup

# Update upstream configuration
cat > $NGINX_CONFIG_DIR/mlops-app << EOF
upstream mlops_backend {
    server localhost:$NEW_PORT;
}

server {
    listen 80;
    server_name _;

    # Health check endpoint (bypass load balancer)
    location /health {
        proxy_pass http://localhost:$NEW_PORT/health;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        access_log off;
    }

    # Main application
    location / {
        proxy_pass http://mlops_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Connection settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # Metrics endpoint for monitoring
    location /metrics {
        proxy_pass http://localhost:$NEW_PORT/metrics;
        proxy_set_header Host \$host;
        allow 10.0.0.0/8;
        allow 172.16.0.0/12;
        allow 192.168.0.0/16;
        deny all;
    }
}
EOF

# Test nginx configuration
nginx -t || {
    echo "❌ Nginx configuration test failed"
    cp $NGINX_CONFIG_DIR/mlops-app.backup $NGINX_CONFIG_DIR/mlops-app
    exit 1
}

# Reload nginx
systemctl reload nginx

# Final health check through load balancer
echo "🌐 Final health check through load balancer..."
sleep 10

for i in {1..5}; do
    if curl -f $HEALTH_CHECK_URL/health > /dev/null 2>&1; then
        echo "✅ Load balancer health check passed!"
        break
    else
        echo "⏳ Load balancer health check attempt $i failed, retrying..."
        sleep 10
        if [ $i -eq 5 ]; then
            echo "❌ Load balancer health check failed, rolling back..."
            
            # Rollback nginx config
            cp $NGINX_CONFIG_DIR/mlops-app.backup $NGINX_CONFIG_DIR/mlops-app
            nginx -t && systemctl reload nginx
            
            # Stop new container
            docker stop $NEW_CONTAINER
            docker rm $NEW_CONTAINER
            exit 1
        fi
    fi
done

# Wait a bit more to ensure stability
echo "⏱️  Monitoring for 2 minutes to ensure stability..."
sleep 120

# Final verification
if curl -f $HEALTH_CHECK_URL/health > /dev/null 2>&1; then
    echo "✅ Deployment stable, cleaning up old environment..."
    
    # Stop old container
    docker stop $CURRENT_CONTAINER || true
    docker rm $CURRENT_CONTAINER || true
    
    # Clean up old nginx backup
    rm -f $NGINX_CONFIG_DIR/mlops-app.backup
    
    # Update current environment marker
    echo $NEW_ENV > $CURRENT_UPSTREAM_FILE
    
    # Send success notification
    aws sns publish \
        --topic-arn "$SNS_TOPIC_ARN" \
        --message "Blue-Green deployment completed successfully. Active environment: $NEW_ENV. Image: $IMAGE_URI" \
        --subject "MLOps Blue-Green Deployment Success" || echo "SNS notification failed"
    
    echo "🎉 Blue-Green deployment completed successfully!"
    echo "🟢 Active environment: $NEW_ENV"
    echo "🌐 Application URL: $HEALTH_CHECK_URL"
    
else
    echo "❌ Final verification failed, something went wrong"
    exit 1
fi