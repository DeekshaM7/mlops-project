#!/bin/bash
set -e

# MLOps Monitoring Setup Script
# Sets up CloudWatch monitoring, logging, and alerting for deployed models

# Configuration
PROJECT_NAME="water-potability-classifier"
ENVIRONMENT="${ENVIRONMENT:-production}"
AWS_REGION="${AWS_REGION:-us-east-1}"
NOTIFICATION_EMAIL="${NOTIFICATION_EMAIL:-admin@example.com}"
STACK_NAME="${PROJECT_NAME}-${ENVIRONMENT}-monitoring"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI not found. Please install AWS CLI."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Please configure AWS credentials."
        exit 1
    fi
    
    # Check CloudFormation template
    if [ ! -f "infrastructure/monitoring.yaml" ]; then
        log_error "Monitoring CloudFormation template not found at infrastructure/monitoring.yaml"
        exit 1
    fi
    
    log_success "Prerequisites check completed"
}

validate_template() {
    log_info "Validating CloudFormation template..."
    
    if aws cloudformation validate-template \
        --template-body file://infrastructure/monitoring.yaml \
        --region $AWS_REGION > /dev/null; then
        log_success "CloudFormation template is valid"
    else
        log_error "CloudFormation template validation failed"
        exit 1
    fi
}

deploy_monitoring_stack() {
    log_info "Deploying monitoring stack: $STACK_NAME"
    
    # Check if stack exists
    if aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION &> /dev/null; then
        
        log_info "Stack exists. Updating..."
        aws cloudformation update-stack \
            --stack-name $STACK_NAME \
            --template-body file://infrastructure/monitoring.yaml \
            --parameters \
                ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
                ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME \
                ParameterKey=NotificationEmail,ParameterValue=$NOTIFICATION_EMAIL \
            --capabilities CAPABILITY_IAM \
            --region $AWS_REGION
        
        log_info "Waiting for stack update to complete..."
        aws cloudformation wait stack-update-complete \
            --stack-name $STACK_NAME \
            --region $AWS_REGION
            
    else
        log_info "Creating new stack..."
        aws cloudformation create-stack \
            --stack-name $STACK_NAME \
            --template-body file://infrastructure/monitoring.yaml \
            --parameters \
                ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
                ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME \
                ParameterKey=NotificationEmail,ParameterValue=$NOTIFICATION_EMAIL \
            --capabilities CAPABILITY_IAM \
            --region $AWS_REGION
        
        log_info "Waiting for stack creation to complete..."
        aws cloudformation wait stack-create-complete \
            --stack-name $STACK_NAME \
            --region $AWS_REGION
    fi
    
    log_success "Monitoring stack deployed successfully"
}

get_stack_outputs() {
    log_info "Getting stack outputs..."
    
    DASHBOARD_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`DashboardURL`].OutputValue' \
        --output text)
    
    SNS_TOPIC_ARN=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`SNSTopicArn`].OutputValue' \
        --output text)
    
    APPLICATION_LOG_GROUP=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`ApplicationLogGroup`].OutputValue' \
        --output text)
    
    MODEL_LOG_GROUP=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`ModelInferenceLogGroup`].OutputValue' \
        --output text)
    
    GOVERNANCE_LOG_GROUP=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`GovernanceLogGroup`].OutputValue' \
        --output text)
}

create_monitoring_config() {
    log_info "Creating monitoring configuration file..."
    
    cat > monitoring/config.json << EOF
{
  "environment": "$ENVIRONMENT",
  "region": "$AWS_REGION",
  "project_name": "$PROJECT_NAME",
  "stack_name": "$STACK_NAME",
  "dashboard_url": "$DASHBOARD_URL",
  "sns_topic_arn": "$SNS_TOPIC_ARN",
  "log_groups": {
    "application": "$APPLICATION_LOG_GROUP",
    "model_inference": "$MODEL_LOG_GROUP",
    "governance": "$GOVERNANCE_LOG_GROUP"
  },
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
    
    log_success "Monitoring configuration saved to monitoring/config.json"
}

setup_log_forwarding() {
    log_info "Setting up log forwarding configuration..."
    
    # Create CloudWatch agent configuration
    cat > monitoring/cloudwatch-agent-config.json << EOF
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/app/logs/application.log",
            "log_group_name": "$APPLICATION_LOG_GROUP",
            "log_stream_name": "{instance_id}/application",
            "timestamp_format": "%Y-%m-%d %H:%M:%S"
          },
          {
            "file_path": "/app/logs/model-inference.log",
            "log_group_name": "$MODEL_LOG_GROUP",
            "log_stream_name": "{instance_id}/model-inference",
            "timestamp_format": "%Y-%m-%d %H:%M:%S"
          },
          {
            "file_path": "/app/logs/governance.log",
            "log_group_name": "$GOVERNANCE_LOG_GROUP",
            "log_stream_name": "{instance_id}/governance",
            "timestamp_format": "%Y-%m-%d %H:%M:%S"
          }
        ]
      }
    }
  },
  "metrics": {
    "namespace": "$PROJECT_NAME/Application",
    "metrics_collected": {
      "cpu": {
        "measurement": [
          "cpu_usage_idle",
          "cpu_usage_iowait",
          "cpu_usage_user",
          "cpu_usage_system"
        ],
        "metrics_collection_interval": 60,
        "totalcpu": false
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
      "diskio": {
        "measurement": [
          "io_time"
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
    
    log_success "CloudWatch agent configuration created"
}

test_monitoring() {
    log_info "Testing monitoring setup..."
    
    # Test log group creation
    for log_group in "$APPLICATION_LOG_GROUP" "$MODEL_LOG_GROUP" "$GOVERNANCE_LOG_GROUP"; do
        if aws logs describe-log-groups \
            --log-group-name-prefix "$log_group" \
            --region $AWS_REGION | grep -q "$log_group"; then
            log_success "Log group $log_group exists"
        else
            log_error "Log group $log_group not found"
        fi
    done
    
    # Test SNS topic
    if aws sns get-topic-attributes \
        --topic-arn "$SNS_TOPIC_ARN" \
        --region $AWS_REGION > /dev/null 2>&1; then
        log_success "SNS topic is accessible"
    else
        log_error "SNS topic not accessible"
    fi
    
    # Send a test log entry
    aws logs create-log-stream \
        --log-group-name "$APPLICATION_LOG_GROUP" \
        --log-stream-name "test-stream" \
        --region $AWS_REGION 2>/dev/null || true
    
    aws logs put-log-events \
        --log-group-name "$APPLICATION_LOG_GROUP" \
        --log-stream-name "test-stream" \
        --log-events timestamp=$(date +%s000),message="Test log entry from monitoring setup" \
        --region $AWS_REGION > /dev/null 2>&1 || true
    
    log_success "Test log entry sent"
}

print_summary() {
    log_success "🎉 Monitoring setup completed successfully!"
    echo
    echo "📊 CloudWatch Dashboard: $DASHBOARD_URL"
    echo "📧 SNS Topic ARN: $SNS_TOPIC_ARN"
    echo "📝 Application Log Group: $APPLICATION_LOG_GROUP"
    echo "🤖 Model Inference Log Group: $MODEL_LOG_GROUP"
    echo "⚖️  Governance Log Group: $GOVERNANCE_LOG_GROUP"
    echo
    echo "Next steps:"
    echo "1. Confirm SNS email subscription in your inbox"
    echo "2. View the CloudWatch dashboard using the URL above"
    echo "3. Configure your application to send logs to the created log groups"
    echo "4. Test alerts by triggering some monitoring conditions"
    echo
    echo "Configuration saved to: monitoring/config.json"
}

main() {
    log_info "🚀 Starting MLOps monitoring setup..."
    echo "Environment: $ENVIRONMENT"
    echo "Region: $AWS_REGION"
    echo "Project: $PROJECT_NAME"
    echo "Notification Email: $NOTIFICATION_EMAIL"
    echo
    
    check_prerequisites
    validate_template
    deploy_monitoring_stack
    get_stack_outputs
    create_monitoring_config
    setup_log_forwarding
    test_monitoring
    print_summary
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -r|--region)
            AWS_REGION="$2"
            shift 2
            ;;
        --email)
            NOTIFICATION_EMAIL="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  -e, --environment ENV    Environment (development/staging/production)"
            echo "  -r, --region REGION      AWS region"
            echo "  --email EMAIL           Notification email address"
            echo "  -h, --help              Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

main