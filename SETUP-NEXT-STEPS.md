# Next Steps After setup-aws.sh

After successfully running `setup-aws.sh`, complete these steps to finish your CI/CD pipeline setup:

## 📋 Prerequisites Completed ✅
- AWS infrastructure created (S3, ECR, VPC, Security Group, IAM roles)
- AWS credentials configured
- Account ID: 533267234773
- Region: ap-south-1

---

## 🔧 Step 1: Update Environment Variables

Create a `.env` file in the project root with the resource IDs from setup-aws.sh output:

```bash
# AWS Configuration
AWS_REGION=ap-south-1
AWS_ACCOUNT_ID=533267234773
AWS_ACCESS_KEY_ID=<from your credentials file>
AWS_SECRET_ACCESS_KEY=<from your credentials file>

# S3 Configuration
S3_BUCKET_NAME=water-quality-ml-dvc-data

# ECR Configuration
ECR_REGISTRY=533267234773.dkr.ecr.ap-south-1.amazonaws.com
ECR_REPOSITORY=water-quality-ml

# VPC & Network (from setup-aws.sh output)
VPC_ID=<copy from output>
SUBNET_ID=<copy from output>
SECURITY_GROUP_ID=<copy from output>

# IAM Configuration
IAM_ROLE_NAME=water-quality-ml-ec2-role
INSTANCE_PROFILE_NAME=water-quality-ml-ec2-profile

# MLflow Configuration
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_S3_ENDPOINT_URL=https://s3.ap-south-1.amazonaws.com

# Model Configuration
MODEL_NAME=water-potability-classifier
MODEL_REGISTRY=s3://water-quality-ml-dvc-data/models
```

**Run this command to create the file:**
```powershell
# In PowerShell (project root)
@"
AWS_REGION=ap-south-1
AWS_ACCOUNT_ID=533267234773
S3_BUCKET_NAME=water-quality-ml-dvc-data
ECR_REGISTRY=533267234773.dkr.ecr.ap-south-1.amazonaws.com
ECR_REPOSITORY=water-quality-ml
"@ | Out-File -FilePath .env -Encoding utf8
```

---

## 🗂️ Step 2: Configure DVC with S3

Configure DVC to use your S3 bucket for data versioning:

```powershell
# Add S3 remote
dvc remote add -d origin s3://water-quality-ml-dvc-data/dvc-storage

# Configure AWS credentials for DVC
dvc remote modify origin region ap-south-1

# Push your data to S3
dvc push
```

**Verify DVC configuration:**
```powershell
# Check remote configuration
dvc remote list

# Test S3 access
aws s3 ls s3://water-quality-ml-dvc-data
```

---

## 🐳 Step 3: Test ECR Access

Login to ECR and verify you can push images:

```powershell
# Login to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 533267234773.dkr.ecr.ap-south-1.amazonaws.com

# Test ECR access
aws ecr describe-repositories --repository-names water-quality-ml --region ap-south-1
```

---

## 🔐 Step 4: Add GitHub Secrets

Go to your GitHub repository: `https://github.com/cvkchris/mlops-project`

Navigate to: **Settings → Secrets and variables → Actions → New repository secret**

Add these **10 required secrets**:

| Secret Name | Value | Where to Find |
|------------|-------|---------------|
| `AWS_ACCESS_KEY_ID` | Your AWS access key | From `mlops-user_accessKeys.csv` |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key | From `mlops-user_accessKeys.csv` |
| `AWS_REGION` | `ap-south-1` | From setup-aws.sh output |
| `AWS_ACCOUNT_ID` | `533267234773` | From setup-aws.sh output |
| `ECR_REPOSITORY` | `water-quality-ml` | From setup-aws.sh output |
| `ECR_REGISTRY` | `533267234773.dkr.ecr.ap-south-1.amazonaws.com` | From setup-aws.sh output |
| `S3_BUCKET_NAME` | `water-quality-ml-dvc-data` | From setup-aws.sh output |
| `VPC_ID` | `vpc-xxxxx` | Copy from setup-aws.sh output |
| `SUBNET_ID` | `subnet-xxxxx` | Copy from setup-aws.sh output |
| `SECURITY_GROUP_ID` | `sg-xxxxx` | Copy from setup-aws.sh output |

**Quick command to view your credentials:**
```powershell
# View AWS credentials (be careful not to share!)
Get-Content mlops-user_accessKeys.csv
```

---

## 🚀 Step 5: Update GitHub Workflow

The workflow file `.github/workflows/complete-mlops-pipeline.yml` uses these secrets. Verify the configuration:

```powershell
# Check workflow file
cat .github/workflows/complete-mlops-pipeline.yml | Select-String "secrets"
```

**Key workflow environment variables to update:**

Open `.github/workflows/complete-mlops-pipeline.yml` and ensure:
```yaml
env:
  AWS_REGION: ap-south-1  # Change from us-east-1
  ECR_REPOSITORY: water-quality-ml
  MODEL_NAME: water-potability-classifier
```

---

## 🖥️ Step 6: Launch EC2 Instance (Optional)

If you need a deployment server, launch an EC2 instance:

```bash
# Get the latest Amazon Linux 2023 AMI for ap-south-1
aws ec2 describe-images \
  --owners amazon \
  --filters "Name=name,Values=al2023-ami-2023*" "Name=architecture,Values=x86_64" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
  --output text \
  --region ap-south-1

# Launch EC2 instance (replace ami-xxxxx with output from above)
aws ec2 run-instances \
  --image-id ami-068af95af805265b0 \
  --instance-type t3.medium \
  --subnet-id subnet-040f040c3fb78dcb9 \
  --security-group-ids sg-00b9fa5de867bb51c \
  --iam-instance-profile Name=water-quality-ml-ec2-profile \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=water-quality-ml-instance}]' \
  --region ap-south-1
```

---

## ✅ Step 7: Test the CI/CD Pipeline

### Test Locally First

```powershell
# Run tests
python -m pytest tests/ -v

# Build Docker image
docker build -f app/Dockerfile -t water-quality-ml:local .

# Test container locally
docker run -p 8000:8000 water-quality-ml:local
```

### Trigger GitHub Actions

```powershell
# Commit and push changes
git add .
git commit -m "Configure CI/CD pipeline with AWS infrastructure"
git push origin master
```

Go to: `https://github.com/cvkchris/mlops-project/actions`

You should see the pipeline running with these stages:
1. ✅ Code Quality & Unit Tests
2. ✅ Data Pipeline Validation
3. ✅ Model Training & Versioning
4. ✅ Docker Build & Push to ECR
5. ✅ Model Deployment
6. ✅ Integration Tests

---

## 📊 Step 8: Monitor & Verify

### Verify S3 Storage
```powershell
# List S3 bucket contents
aws s3 ls s3://water-quality-ml-dvc-data --recursive

# Check DVC storage
aws s3 ls s3://water-quality-ml-dvc-data/dvc-storage/
```

### Verify ECR Images
```powershell
# List Docker images in ECR
aws ecr list-images --repository-name water-quality-ml --region ap-south-1

# Get image details
aws ecr describe-images --repository-name water-quality-ml --region ap-south-1
```

### Verify IAM Roles
```powershell
# List IAM role
aws iam get-role --role-name water-quality-ml-ec2-role

# List attached policies
aws iam list-attached-role-policies --role-name water-quality-ml-ec2-role
```

---

## 🔍 Troubleshooting

### Issue: GitHub Actions fails with "No such secret"
**Solution:** Double-check all 10 secrets are added in GitHub Settings → Secrets

### Issue: ECR push fails with "authentication required"
**Solution:** Run the ECR login command again:
```powershell
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 533267234773.dkr.ecr.ap-south-1.amazonaws.com
```

### Issue: DVC push fails with "access denied"
**Solution:** Check AWS credentials and S3 bucket permissions:
```powershell
# Test S3 access
aws s3 ls s3://water-quality-ml-dvc-data

# Test write access
echo "test" | aws s3 cp - s3://water-quality-ml-dvc-data/test.txt
aws s3 rm s3://water-quality-ml-dvc-data/test.txt
```

### Issue: Pipeline runs but deployment fails
**Solution:** Check EC2 instance status and security group rules:
```powershell
# List running instances
aws ec2 describe-instances --filters "Name=tag:Name,Values=water-quality-ml-instance" --region ap-south-1

# Check security group rules
aws ec2 describe-security-groups --group-ids <SECURITY_GROUP_ID> --region ap-south-1
```

---

## 📚 Additional Resources

- **AWS Setup Checklist:** `infrastructure/AWS-SETUP-CHECKLIST.md`
- **GitHub Workflow:** `.github/workflows/complete-mlops-pipeline.yml`
- **DVC Documentation:** https://dvc.org/doc/command-reference/remote/add
- **ECR Documentation:** https://docs.aws.amazon.com/ecr/

---

## 🎯 Quick Verification Checklist

- [ ] `.env` file created with all variables
- [ ] DVC remote configured and data pushed to S3
- [ ] ECR login successful
- [ ] All 10 GitHub secrets added
- [ ] Workflow file updated with correct region
- [ ] Local tests passing
- [ ] Docker build successful
- [ ] First commit pushed to trigger pipeline
- [ ] GitHub Actions running successfully
- [ ] ECR contains the built image

---

## 🚦 What's Next?

After completing these steps, your CI/CD pipeline is fully operational! Every push to `master` will:

1. Run code quality checks and tests
2. Validate data pipeline
3. Train and version models with MLflow
4. Build Docker image
5. Push to ECR
6. Deploy model
7. Run integration tests

**You're ready to start developing your ML models with full MLOps automation!** 🎉
