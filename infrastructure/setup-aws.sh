#!/bin/bash
# AWS Infrastructure Setup Script for MLOps Pipeline

set -e

# Configuration
AWS_REGION="${AWS_REGION}"  # Can be overridden with environment variable
PROJECT_NAME="water-quality-ml"
S3_BUCKET="${PROJECT_NAME}-dvc-data-$(date +%s)"
ECR_REPO="${PROJECT_NAME}"

echo "🚀 Setting up AWS infrastructure for MLOps pipeline..."
echo "📍 Region: $AWS_REGION"
echo "📦 Project: $PROJECT_NAME"
echo ""

# Verify AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ Error: AWS credentials not configured!"
    echo "Please run 'aws configure' first."
    exit 1
fi

echo "✅ AWS credentials verified"
echo "Account: $(aws sts get-caller-identity --query Account --output text)"
echo ""

# 1. Create S3 bucket for DVC data storage
echo "📦 Creating S3 bucket: $S3_BUCKET"
aws s3 mb s3://$S3_BUCKET --region $AWS_REGION

# Enable versioning for data lineage
aws s3api put-bucket-versioning \
    --bucket $S3_BUCKET \
    --versioning-configuration Status=Enabled

# Create bucket policy for DVC access
cat > bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):root"
            },
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::$S3_BUCKET",
                "arn:aws:s3:::$S3_BUCKET/*"
            ]
        }
    ]
}
EOF

aws s3api put-bucket-policy --bucket $S3_BUCKET --policy file://bucket-policy.json
rm bucket-policy.json

# 2. Create ECR repository for Docker images
echo "🐳 Creating ECR repository: $ECR_REPO"
aws ecr create-repository \
    --repository-name $ECR_REPO \
    --region $AWS_REGION \
    --image-scanning-configuration scanOnPush=true \
    --lifecycle-policy-text '{
        "rules": [{
            "rulePriority": 1,
            "selection": {
                "tagStatus": "untagged",
                "countType": "sinceImagePushed",
                "countUnit": "days",
                "countNumber": 7
            },
            "action": {"type": "expire"}
        }]
    }' || echo "Repository might already exist"

# 3. Create IAM role for EC2 instances
echo "🔐 Creating IAM roles and policies..."

# Create trust policy for EC2
cat > ec2-trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

# Create IAM role
aws iam create-role \
    --role-name ${PROJECT_NAME}-ec2-role \
    --assume-role-policy-document file://ec2-trust-policy.json || echo "Role might already exist"

# Create custom policy for S3 and ECR access
cat > mlops-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::$S3_BUCKET",
                "arn:aws:s3:::$S3_BUCKET/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetAuthorizationToken"
            ],
            "Resource": "*"
        }
    ]
}
EOF

aws iam create-policy \
    --policy-name ${PROJECT_NAME}-mlops-policy \
    --policy-document file://mlops-policy.json || echo "Policy might already exist"

# Attach policies to role
aws iam attach-role-policy \
    --role-name ${PROJECT_NAME}-ec2-role \
    --policy-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/${PROJECT_NAME}-mlops-policy

aws iam attach-role-policy \
    --role-name ${PROJECT_NAME}-ec2-role \
    --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

# Create instance profile
aws iam create-instance-profile \
    --instance-profile-name ${PROJECT_NAME}-ec2-profile || echo "Instance profile might already exist"

aws iam add-role-to-instance-profile \
    --instance-profile-name ${PROJECT_NAME}-ec2-profile \
    --role-name ${PROJECT_NAME}-ec2-role || echo "Role might already be attached"

# Clean up temporary files
rm ec2-trust-policy.json mlops-policy.json

# 4. Create security group for EC2
echo "🔒 Creating security group..."
SECURITY_GROUP_ID=$(aws ec2 create-security-group \
    --group-name ${PROJECT_NAME}-sg \
    --description "Security group for MLOps pipeline" \
    --query 'GroupId' \
    --output text 2>/dev/null || aws ec2 describe-security-groups \
    --group-names ${PROJECT_NAME}-sg \
    --query 'SecurityGroups[0].GroupId' \
    --output text)

# Add rules for SSH and HTTP
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0 || echo "SSH rule might already exist"

aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 8000 \
    --cidr 0.0.0.0/0 || echo "HTTP rule might already exist"

# Output important information
echo ""
echo "✅ Infrastructure setup complete!"
echo ""
echo "📋 Important Information:"
echo "========================="
echo "S3 Bucket: $S3_BUCKET"
echo "ECR Repository: $ECR_REPO"
echo "Security Group ID: $SECURITY_GROUP_ID"
echo "Instance Profile: ${PROJECT_NAME}-ec2-profile"
echo ""
echo "🔧 Next steps:"
echo "1. Update your .dvc/config with the S3 bucket URL"
echo "2. Set up GitHub secrets with AWS credentials"
echo "3. Launch EC2 instance with the created instance profile"
echo "4. Configure MLflow tracking server"
echo ""
echo "GitHub Secrets needed:"
echo "- AWS_ACCESS_KEY_ID"
echo "- AWS_SECRET_ACCESS_KEY"
echo "- ECR_REGISTRY: $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com"
echo "- EC2_HOST: (your EC2 instance IP)"
echo "- EC2_USER: ubuntu (or ec2-user for Amazon Linux)"
echo "- EC2_SSH_KEY: (your private SSH key)"
echo "- MLFLOW_TRACKING_URI: (your MLflow server URL)"