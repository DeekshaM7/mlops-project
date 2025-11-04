#!/bin/bash
# AWS Infrastructure Setup Script for MLOps Pipeline

# Don't exit on error - we'll handle errors gracefully
set +e

# Configuration - Use environment variable or default to ap-south-1
AWS_REGION="${AWS_REGION:-ap-south-1}"
PROJECT_NAME="water-quality-ml"
S3_BUCKET="${S3_BUCKET_NAME:-${PROJECT_NAME}-dvc-data}"
ECR_REPO="${PROJECT_NAME}"

echo "🚀 Setting up AWS infrastructure for MLOps pipeline..."
echo "📍 Region: $AWS_REGION"
echo "📦 Project: $PROJECT_NAME"
echo "🪣 S3 Bucket: $S3_BUCKET"
echo ""

# Verify AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ Error: AWS credentials not configured!"
    echo "Please run 'aws configure' first or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
    exit 1
fi

echo "✅ AWS credentials verified"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "📋 Account ID: $ACCOUNT_ID"
echo ""

# 1. Create S3 bucket for DVC data storage
echo "📦 Checking S3 bucket: $S3_BUCKET"
if aws s3 ls "s3://$S3_BUCKET" &>/dev/null; then
    echo "ℹ️  Bucket already exists: $S3_BUCKET"
else
    echo "Creating S3 bucket..."
    CREATE_OUTPUT=$(aws s3 mb "s3://$S3_BUCKET" --region "$AWS_REGION" 2>&1)
    if [ $? -eq 0 ]; then
        echo "✅ Created bucket: $S3_BUCKET"
    elif echo "$CREATE_OUTPUT" | grep -q "BucketAlreadyOwnedByYou\|BucketAlreadyExists"; then
        echo "ℹ️  Bucket already exists: $S3_BUCKET"
    else
        echo "⚠️  Warning: Could not create bucket. Error: $CREATE_OUTPUT"
    fi
fi

# Enable versioning for data lineage
echo "🔄 Configuring bucket versioning..."
aws s3api put-bucket-versioning \
    --bucket "$S3_BUCKET" \
    --versioning-configuration Status=Enabled \
    --region "$AWS_REGION" &>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Versioning enabled"
else
    echo "ℹ️  Versioning already configured or skipped"
fi

# Enable encryption
echo "🔒 Configuring bucket encryption..."
aws s3api put-bucket-encryption \
    --bucket "$S3_BUCKET" \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            },
            "BucketKeyEnabled": true
        }]
    }' \
    --region "$AWS_REGION" &>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Encryption enabled"
else
    echo "ℹ️  Encryption already configured or skipped"
fi

# Block public access
echo "🚫 Configuring public access block..."
aws s3api put-public-access-block \
    --bucket "$S3_BUCKET" \
    --public-access-block-configuration \
        "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true" \
    --region "$AWS_REGION" &>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Public access blocked"
else
    echo "ℹ️  Public access block already configured or skipped"
fi

echo "✅ S3 bucket configured successfully"
echo ""

# 2. Create ECR repository for Docker images
echo "🐳 Checking ECR repository: $ECR_REPO"
if aws ecr describe-repositories --repository-names "$ECR_REPO" --region "$AWS_REGION" &>/dev/null; then
    echo "ℹ️  ECR repository already exists: $ECR_REPO"
else
    echo "Creating ECR repository..."
    CREATE_OUTPUT=$(aws ecr create-repository \
        --repository-name "$ECR_REPO" \
        --region "$AWS_REGION" \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256 2>&1)
    
    if [ $? -eq 0 ]; then
        echo "✅ Created ECR repository: $ECR_REPO"
    else
        echo "⚠️  Warning: Could not create ECR repository. Error: $CREATE_OUTPUT"
    fi
fi

# Set lifecycle policy
echo "♻️  Configuring lifecycle policy..."

# Create lifecycle policy file
cat > ecr-lifecycle-policy.json << 'EOFPOLICY'
{
    "rules": [{
        "rulePriority": 1,
        "description": "Remove untagged images after 7 days",
        "selection": {
            "tagStatus": "untagged",
            "countType": "sinceImagePushed",
            "countUnit": "days",
            "countNumber": 7
        },
        "action": {"type": "expire"}
    }, {
        "rulePriority": 2,
        "description": "Keep only last 10 tagged images",
        "selection": {
            "tagStatus": "any",
            "countType": "imageCountMoreThan",
            "countNumber": 10
        },
        "action": {"type": "expire"}
    }]
}
EOFPOLICY

# Set lifecycle policy
aws ecr put-lifecycle-policy \
    --repository-name "$ECR_REPO" \
    --region "$AWS_REGION" \
    --lifecycle-policy-text file://ecr-lifecycle-policy.json &>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Lifecycle policy configured"
else
    echo "ℹ️  Lifecycle policy already configured or skipped"
fi

rm -f ecr-lifecycle-policy.json

echo "✅ ECR repository configured successfully"
echo ""

# 3. Create IAM role for EC2 instances
echo "👤 Setting up IAM roles and policies..."

# Create trust policy for EC2
cat > ec2-trust-policy.json << 'EOFTRUST'
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
EOFTRUST

# Create IAM role
ROLE_NAME="${PROJECT_NAME}-ec2-role"
if aws iam get-role --role-name "$ROLE_NAME" &>/dev/null; then
    echo "ℹ️  IAM role already exists: $ROLE_NAME"
else
    CREATE_OUTPUT=$(aws iam create-role \
        --role-name "$ROLE_NAME" \
        --assume-role-policy-document file://ec2-trust-policy.json \
        --description "Role for MLOps EC2 instances" 2>&1)
    if [ $? -eq 0 ]; then
        echo "✅ Created IAM role: $ROLE_NAME"
    else
        echo "⚠️  Warning: Could not create IAM role. Error: $CREATE_OUTPUT"
    fi
fi

# Create custom policy for S3, ECR, and CloudWatch access
POLICY_NAME="${PROJECT_NAME}-mlops-policy"
cat > mlops-policy.json << EOFPOLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3Access",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket",
                "s3:GetBucketLocation"
            ],
            "Resource": [
                "arn:aws:s3:::$S3_BUCKET",
                "arn:aws:s3:::$S3_BUCKET/*"
            ]
        },
        {
            "Sid": "ECRAccess",
            "Effect": "Allow",
            "Action": [
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetAuthorizationToken",
                "ecr:DescribeRepositories",
                "ecr:ListImages"
            ],
            "Resource": "*"
        },
        {
            "Sid": "CloudWatchLogs",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogStreams"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Sid": "CloudWatchMetrics",
            "Effect": "Allow",
            "Action": [
                "cloudwatch:PutMetricData",
                "cloudwatch:GetMetricStatistics",
                "cloudwatch:ListMetrics"
            ],
            "Resource": "*"
        }
    ]
}
EOFPOLICY

# Check if policy exists
POLICY_ARN="arn:aws:iam::$ACCOUNT_ID:policy/$POLICY_NAME"
if aws iam get-policy --policy-arn "$POLICY_ARN" &>/dev/null; then
    echo "ℹ️  IAM policy already exists: $POLICY_NAME"
    # Update policy with new version
    UPDATE_OUTPUT=$(aws iam create-policy-version \
        --policy-arn "$POLICY_ARN" \
        --policy-document file://mlops-policy.json \
        --set-as-default 2>&1)
    if [ $? -eq 0 ]; then
        echo "✅ Updated IAM policy: $POLICY_NAME"
    else
        echo "ℹ️  Policy update skipped (may have too many versions or no changes)"
    fi
else
    CREATE_OUTPUT=$(aws iam create-policy \
        --policy-name "$POLICY_NAME" \
        --policy-document file://mlops-policy.json \
        --description "Policy for MLOps pipeline EC2 instances" 2>&1)
    if [ $? -eq 0 ]; then
        echo "✅ Created IAM policy: $POLICY_NAME"
    else
        echo "⚠️  Warning: Could not create IAM policy. Error: $CREATE_OUTPUT"
    fi
fi

# Attach policies to role
echo "🔗 Attaching policies to role..."
aws iam attach-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-arn "$POLICY_ARN" &>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Attached custom policy"
else
    echo "ℹ️  Custom policy already attached"
fi

aws iam attach-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore &>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Attached SSM policy"
else
    echo "ℹ️  SSM policy already attached"
fi

aws iam attach-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-arn arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy &>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Attached CloudWatch policy"
else
    echo "ℹ️  CloudWatch policy already attached"
fi

# Create instance profile
INSTANCE_PROFILE_NAME="${PROJECT_NAME}-ec2-profile"
if aws iam get-instance-profile --instance-profile-name "$INSTANCE_PROFILE_NAME" &>/dev/null; then
    echo "ℹ️  Instance profile already exists: $INSTANCE_PROFILE_NAME"
else
    CREATE_OUTPUT=$(aws iam create-instance-profile \
        --instance-profile-name "$INSTANCE_PROFILE_NAME" 2>&1)
    
    if [ $? -eq 0 ]; then
        echo "✅ Created instance profile: $INSTANCE_PROFILE_NAME"
        
        # Wait for instance profile to be available
        echo "⏳ Waiting for instance profile to be ready..."
        sleep 10
        
        aws iam add-role-to-instance-profile \
            --instance-profile-name "$INSTANCE_PROFILE_NAME" \
            --role-name "$ROLE_NAME" &>/dev/null
        if [ $? -eq 0 ]; then
            echo "✅ Added role to instance profile"
        else
            echo "ℹ️  Role already added to instance profile"
        fi
    else
        echo "⚠️  Warning: Could not create instance profile. Error: $CREATE_OUTPUT"
    fi
fi

# Clean up temporary files
rm -f ec2-trust-policy.json mlops-policy.json

echo "✅ IAM configuration completed"
echo ""

# 4. Check for VPC and create if needed
echo "🌐 Checking for VPC..."

# Try to get default VPC
VPC_ID=$(aws ec2 describe-vpcs \
    --filters "Name=is-default,Values=true" \
    --query 'Vpcs[0].VpcId' \
    --output text \
    --region "$AWS_REGION" 2>/dev/null)

if [ "$VPC_ID" = "None" ] || [ -z "$VPC_ID" ]; then
    echo "⚠️  No default VPC found. Creating VPC..."
    
    # Create VPC
    VPC_ID=$(aws ec2 create-vpc \
        --cidr-block 10.0.0.0/16 \
        --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=${PROJECT_NAME}-vpc}]" \
        --query 'Vpc.VpcId' \
        --output text \
        --region "$AWS_REGION" 2>/dev/null)
    
    if [ -n "$VPC_ID" ] && [ "$VPC_ID" != "None" ]; then
        echo "✅ Created VPC: $VPC_ID"
        
        # Enable DNS hostnames
        aws ec2 modify-vpc-attribute \
            --vpc-id "$VPC_ID" \
            --enable-dns-hostnames \
            --region "$AWS_REGION" &>/dev/null
        
        # Create Internet Gateway
        IGW_ID=$(aws ec2 create-internet-gateway \
            --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=${PROJECT_NAME}-igw}]" \
            --query 'InternetGateway.InternetGatewayId' \
            --output text \
            --region "$AWS_REGION" 2>/dev/null)
        
        # Attach Internet Gateway to VPC
        aws ec2 attach-internet-gateway \
            --vpc-id "$VPC_ID" \
            --internet-gateway-id "$IGW_ID" \
            --region "$AWS_REGION" &>/dev/null
        
        echo "✅ Created and attached Internet Gateway: $IGW_ID"
        
        # Create public subnet
        SUBNET_ID=$(aws ec2 create-subnet \
            --vpc-id "$VPC_ID" \
            --cidr-block 10.0.1.0/24 \
            --availability-zone "${AWS_REGION}a" \
            --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${PROJECT_NAME}-public-subnet}]" \
            --query 'Subnet.SubnetId' \
            --output text \
            --region "$AWS_REGION" 2>/dev/null)
        
        echo "✅ Created subnet: $SUBNET_ID"
        
        # Enable auto-assign public IP
        aws ec2 modify-subnet-attribute \
            --subnet-id "$SUBNET_ID" \
            --map-public-ip-on-launch \
            --region "$AWS_REGION" &>/dev/null
        
        # Create route table
        ROUTE_TABLE_ID=$(aws ec2 create-route-table \
            --vpc-id "$VPC_ID" \
            --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=${PROJECT_NAME}-public-rt}]" \
            --query 'RouteTable.RouteTableId' \
            --output text \
            --region "$AWS_REGION" 2>/dev/null)
        
        # Create route to internet gateway
        aws ec2 create-route \
            --route-table-id "$ROUTE_TABLE_ID" \
            --destination-cidr-block 0.0.0.0/0 \
            --gateway-id "$IGW_ID" \
            --region "$AWS_REGION" &>/dev/null
        
        # Associate route table with subnet
        aws ec2 associate-route-table \
            --subnet-id "$SUBNET_ID" \
            --route-table-id "$ROUTE_TABLE_ID" \
            --region "$AWS_REGION" &>/dev/null
        
        echo "✅ Configured routing for subnet"
    else
        echo "⚠️  Warning: Could not create VPC"
        exit 1
    fi
else
    echo "✅ Using existing VPC: $VPC_ID"
    
    # Get existing subnet
    SUBNET_ID=$(aws ec2 describe-subnets \
        --filters "Name=vpc-id,Values=$VPC_ID" "Name=default-for-az,Values=true" \
        --query 'Subnets[0].SubnetId' \
        --output text \
        --region "$AWS_REGION" 2>/dev/null)
    
    if [ -n "$SUBNET_ID" ] && [ "$SUBNET_ID" != "None" ]; then
        echo "✅ Using existing subnet: $SUBNET_ID"
    else
        echo "⚠️  Warning: Could not find subnet in VPC"
    fi
fi

echo "✅ VPC configuration completed"
echo ""

# 5. Create security group for EC2
echo "🔒 Checking security group..."
SG_NAME="${PROJECT_NAME}-sg"

# Check if security group exists
SECURITY_GROUP_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=$SG_NAME" "Name=vpc-id,Values=$VPC_ID" \
    --query 'SecurityGroups[0].GroupId' \
    --output text \
    --region "$AWS_REGION" 2>/dev/null)

if [ "$SECURITY_GROUP_ID" = "None" ] || [ -z "$SECURITY_GROUP_ID" ]; then
    CREATE_OUTPUT=$(aws ec2 create-security-group \
        --group-name "$SG_NAME" \
        --description "Security group for MLOps pipeline" \
        --vpc-id "$VPC_ID" \
        --query 'GroupId' \
        --output text \
        --region "$AWS_REGION" 2>&1)
    if [ $? -eq 0 ]; then
        SECURITY_GROUP_ID="$CREATE_OUTPUT"
        echo "✅ Created security group: $SECURITY_GROUP_ID"
    else
        echo "⚠️  Warning: Could not create security group. Error: $CREATE_OUTPUT"
    fi
else
    echo "ℹ️  Security group already exists: $SECURITY_GROUP_ID"
fi

# Add ingress rules
echo "🚪 Configuring security group rules..."

# SSH (port 22)
aws ec2 authorize-security-group-ingress \
    --group-id "$SECURITY_GROUP_ID" \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0 \
    --region "$AWS_REGION" &>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Added SSH rule (port 22)"
else
    echo "ℹ️  SSH rule already exists"
fi

# HTTP (port 80)
aws ec2 authorize-security-group-ingress \
    --group-id "$SECURITY_GROUP_ID" \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0 \
    --region "$AWS_REGION" &>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Added HTTP rule (port 80)"
else
    echo "ℹ️  HTTP rule already exists"
fi

# HTTPS (port 443)
aws ec2 authorize-security-group-ingress \
    --group-id "$SECURITY_GROUP_ID" \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0 \
    --region "$AWS_REGION" &>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Added HTTPS rule (port 443)"
else
    echo "ℹ️  HTTPS rule already exists"
fi

# Flask/FastAPI (port 5000)
aws ec2 authorize-security-group-ingress \
    --group-id "$SECURITY_GROUP_ID" \
    --protocol tcp \
    --port 5000 \
    --cidr 0.0.0.0/0 \
    --region "$AWS_REGION" &>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Added port 5000 rule"
else
    echo "ℹ️  Port 5000 rule already exists"
fi

# Application (port 8000)
aws ec2 authorize-security-group-ingress \
    --group-id "$SECURITY_GROUP_ID" \
    --protocol tcp \
    --port 8000 \
    --cidr 0.0.0.0/0 \
    --region "$AWS_REGION" &>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Added port 8000 rule"
else
    echo "ℹ️  Port 8000 rule already exists"
fi

echo "✅ Security group configured"
echo ""

# Get ECR login command
ECR_REGISTRY="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

# Output important information
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ Infrastructure setup complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📋 Resource Summary:"
echo "────────────────────────────────────────────────────────────────"
echo "AWS Region:           $AWS_REGION"
echo "AWS Account ID:       $ACCOUNT_ID"
echo "VPC ID:               $VPC_ID"
echo "Subnet ID:            $SUBNET_ID"
echo "S3 Bucket:            $S3_BUCKET"
echo "ECR Repository:       $ECR_REPO"
echo "ECR Registry:         $ECR_REGISTRY"
echo "Security Group ID:    $SECURITY_GROUP_ID"
echo "IAM Role:             $ROLE_NAME"
echo "Instance Profile:     $INSTANCE_PROFILE_NAME"
echo ""
echo "🔧 Next Steps:"
echo "────────────────────────────────────────────────────────────────"
echo "1. Configure DVC to use S3:"
echo "   dvc remote add -d origin s3://$S3_BUCKET/dvc-storage"
echo "   dvc push"
echo ""
echo "2. Login to ECR:"
echo "   aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY"
echo ""
echo "3. Add these secrets to your GitHub repository:"
echo "   Settings → Secrets and variables → Actions → New repository secret"
echo ""
echo "   AWS_ACCESS_KEY_ID: <your-access-key>"
echo "   AWS_SECRET_ACCESS_KEY: <your-secret-key>"
echo "   AWS_REGION: $AWS_REGION"
echo "   AWS_ACCOUNT_ID: $ACCOUNT_ID"
echo "   ECR_REPOSITORY: $ECR_REPO"
echo "   ECR_REGISTRY: $ECR_REGISTRY"
echo "   S3_BUCKET_NAME: $S3_BUCKET"
echo "   VPC_ID: $VPC_ID"
echo "   SUBNET_ID: $SUBNET_ID"
echo "   SECURITY_GROUP_ID: $SECURITY_GROUP_ID"
echo ""
echo "4. Update your .env file:"
echo "   AWS_REGION=$AWS_REGION"
echo "   S3_BUCKET_NAME=$S3_BUCKET"
echo "   AWS_ACCOUNT_ID=$ACCOUNT_ID"
echo "   ECR_REGISTRY=$ECR_REGISTRY"
echo "   VPC_ID=$VPC_ID"
echo "   SUBNET_ID=$SUBNET_ID"
echo ""
echo "5. Launch EC2 instance using the VPC and subnet:"
echo "   aws ec2 run-instances \\"
echo "     --image-id ami-0c7217cdde317cfec \\"
echo "     --instance-type t3.medium \\"
echo "     --subnet-id $SUBNET_ID \\"
echo "     --security-group-ids $SECURITY_GROUP_ID \\"
echo "     --iam-instance-profile Name=$INSTANCE_PROFILE_NAME \\"
echo "     --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=${PROJECT_NAME}-instance}]'"
echo ""
echo "6. Test S3 access:"
echo "   aws s3 ls s3://$S3_BUCKET"
echo ""
echo "7. Test ECR access:"
echo "   aws ecr describe-repositories --repository-names $ECR_REPO"
echo ""
echo "════════════════════════════════════════════════════════════════"