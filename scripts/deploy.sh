#!/bin/bash
# Deployment script for staging/production environments

set -euo pipefail

ENVIRONMENT=${1:-staging}
IMAGE_URI=${2:-"latest"}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 Starting deployment to $ENVIRONMENT environment"
echo "📦 Image: $IMAGE_URI"

# Load environment-specific configuration
if [ -f "$PROJECT_ROOT/configs/$ENVIRONMENT.env" ]; then
    source "$PROJECT_ROOT/configs/$ENVIRONMENT.env"
fi

# Set default values
CONTAINER_NAME="${CONTAINER_NAME:-mlops-app-$ENVIRONMENT}"
PORT="${PORT:-8000}"
HEALTH_CHECK_URL="${HEALTH_CHECK_URL:-http://localhost:$PORT/health}"

# AWS ECR login
echo "🔐 Logging into AWS ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# Pull latest image
echo "📥 Pulling Docker image..."
docker pull $IMAGE_URI

# Stop existing container
echo "🛑 Stopping existing container..."
docker stop $CONTAINER_NAME || echo "Container $CONTAINER_NAME not running"
docker rm $CONTAINER_NAME || echo "Container $CONTAINER_NAME not found"

# Start new container
echo "🏃 Starting new container..."
docker run -d \
    --name $CONTAINER_NAME \
    --restart unless-stopped \
    -p $PORT:8000 \
    -e ENVIRONMENT=$ENVIRONMENT \
    -e MLFLOW_TRACKING_URI="$MLFLOW_TRACKING_URI" \
    -e MLFLOW_TRACKING_USERNAME="$MLFLOW_TRACKING_USERNAME" \
    -e MLFLOW_TRACKING_PASSWORD="$MLFLOW_TRACKING_PASSWORD" \
    -e AWS_REGION="$AWS_REGION" \
    -e MODEL_VERSION="$MODEL_VERSION" \
    -v /opt/mlops-$ENVIRONMENT/logs:/app/logs \
    -v /opt/mlops-$ENVIRONMENT/data:/app/data \
    --log-driver=awslogs \
    --log-opt awslogs-group="/aws/ec2/mlops-$ENVIRONMENT" \
    --log-opt awslogs-region="$AWS_REGION" \
    --log-opt awslogs-stream="\$(hostname)" \
    $IMAGE_URI

# Health check
echo "🏥 Performing health check..."
sleep 30

for i in {1..10}; do
    if curl -f $HEALTH_CHECK_URL > /dev/null 2>&1; then
        echo "✅ Health check passed!"
        break
    else
        echo "⏳ Health check attempt $i failed, retrying..."
        sleep 10
        if [ $i -eq 10 ]; then
            echo "❌ Health check failed after 10 attempts"
            docker logs $CONTAINER_NAME
            exit 1
        fi
    fi
done

# Setup log forwarding to CloudWatch
echo "📊 Setting up CloudWatch logging..."
docker exec $CONTAINER_NAME sh -c "
    cat > /app/cloudwatch-config.json << EOF
{
    \"logs\": {
        \"logs_collected\": {
            \"files\": {
                \"collect_list\": [
                    {
                        \"file_path\": \"/app/logs/access.log\",
                        \"log_group_name\": \"/aws/ec2/mlops-$ENVIRONMENT/access\",
                        \"log_stream_name\": \"{instance_id}\"
                    },
                    {
                        \"file_path\": \"/app/logs/error.log\",
                        \"log_group_name\": \"/aws/ec2/mlops-$ENVIRONMENT/error\",
                        \"log_stream_name\": \"{instance_id}\"
                    }
                ]
            }
        }
    }
}
EOF
"

# Send deployment notification
echo "📧 Sending deployment notification..."
aws sns publish \
    --topic-arn "$SNS_TOPIC_ARN" \
    --message "Deployment completed successfully for $ENVIRONMENT environment. Image: $IMAGE_URI" \
    --subject "MLOps Deployment - $ENVIRONMENT" || echo "SNS notification failed"

echo "🎉 Deployment to $ENVIRONMENT completed successfully!"
echo "🌐 Application URL: http://$(curl -s http://169.254.169.254/latest/meta-data/public-hostname):$PORT"
echo "📊 Logs: docker logs $CONTAINER_NAME"