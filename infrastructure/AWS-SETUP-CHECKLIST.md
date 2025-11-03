# AWS Setup Pre-Flight Checklist

## ✅ Complete These Steps Before Running the Setup Script

### Step 1: AWS Account Setup
- [ ] Create AWS account at https://aws.amazon.com/
- [ ] Verify email address
- [ ] Add payment method (Free Tier available for 12 months)
- [ ] Enable MFA (Multi-Factor Authentication) for security

### Step 2: Create IAM User with Required Permissions

**Important:** Don't use your root account credentials!

1. Log into AWS Console → https://console.aws.amazon.com/
2. Navigate to **IAM** service
3. Click **Users** → **Create user**
4. User name: `mlops-admin` (or your preference)
5. Enable **Provide user access to the AWS Management Console** (optional)
6. Click **Next**

**Attach Permissions:**
- [ ] `AdministratorAccess` (for initial setup)
  
  OR create a custom policy group with:
  - [ ] `AmazonS3FullAccess`
  - [ ] `AmazonEC2ContainerRegistryFullAccess`
  - [ ] `IAMFullAccess`
  - [ ] `AmazonEC2FullAccess`
  - [ ] `CloudWatchFullAccess`

7. Click **Create user**
8. Download credentials or note them securely

### Step 3: Generate Access Keys

1. In IAM → Users → Select your user
2. Click **Security credentials** tab
3. Scroll to **Access keys** section
4. Click **Create access key**
5. Select **Command Line Interface (CLI)** as use case
6. Check "I understand..." → **Next**
7. Add description: "MLOps Pipeline Setup"
8. **Create access key**
9. **⚠️ IMPORTANT:** Download the `.csv` file or copy keys immediately
   - Access Key ID: `AKIA...`
   - Secret Access Key: `wJalrXUt...` (only shown once!)

### Step 4: Install Required Software

#### Windows PowerShell (already have ✓)
- You're using PowerShell - good to go!

#### AWS CLI
```powershell
# Check if installed
aws --version

# If not, download and install:
# https://awscli.amazonaws.com/AWSCLIV2.msi
```

#### Git (if not installed)
```powershell
# Check if installed
git --version

# If not, download and install:
# https://git-scm.com/download/win
```

### Step 5: Configure AWS CLI

```powershell
# Run configuration
aws configure

# Enter when prompted:
AWS Access Key ID [None]: AKIA...your-access-key...
AWS Secret Access Key [None]: wJalr...your-secret-key...
Default region name [None]: ap-south-1
Default output format [None]: json
```

### Step 6: Verify AWS Configuration

```powershell
# Test AWS CLI is working
aws sts get-caller-identity

# Expected output:
# {
#     "UserId": "AIDA...",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/mlops-admin"
# }

# Check your current region
aws configure get region

# List S3 buckets (should return empty list or existing buckets)
aws s3 ls
```

### Step 7: Review AWS Free Tier Limits

To avoid unexpected charges, review:
- **S3**: 5GB storage, 20,000 GET requests, 2,000 PUT requests/month
- **EC2**: 750 hours/month of t2.micro or t3.micro instances
- **ECR**: 500MB storage/month
- **Data Transfer**: 100GB outbound/month

Estimated costs for this project: **~$10-30/month** (beyond free tier)

### Step 8: Choose Your AWS Region

Current default: **ap-south-1** (Mumbai, India)

**Popular regions:**
- `us-east-1` - US East (N. Virginia) - Most services, lowest cost
- `us-west-2` - US West (Oregon)
- `eu-west-1` - Europe (Ireland)
- `ap-south-1` - Asia Pacific (Mumbai) ✓ Current
- `ap-southeast-1` - Asia Pacific (Singapore)

To change region in the script:
```powershell
# Edit setup-aws.ps1 and change the Region parameter
# OR pass it when running:
.\infrastructure\setup-aws.ps1 -Region "us-east-1"
```

---

## 🚀 Running the Setup Script

### Option 1: PowerShell (Recommended for Windows)

```powershell
# Navigate to project directory
cd d:\Projects\MLOPS\mlops-project

# Make sure you're in the right directory
Get-Location

# Run the PowerShell script
.\infrastructure\setup-aws.ps1

# Or with custom region:
.\infrastructure\setup-aws.ps1 -Region "us-east-1"
```

### Option 2: Git Bash (Using the .sh script)

```bash
# Open Git Bash in project directory
cd /d/Projects/MLOPS/mlops-project

# Make script executable
chmod +x infrastructure/setup-aws.sh

# Run the bash script
./infrastructure/setup-aws.sh

# Or with custom region:
AWS_REGION=us-east-1 ./infrastructure/setup-aws.sh
```

---

## ✅ Post-Setup Verification

After running the script successfully:

### 1. Verify S3 Bucket Created
```powershell
aws s3 ls
# Should show: water-quality-ml-dvc-data-{timestamp}
```

### 2. Verify ECR Repository Created
```powershell
aws ecr describe-repositories --repository-names water-quality-ml
```

### 3. Verify IAM Role Created
```powershell
aws iam get-role --role-name water-quality-ml-ec2-role
```

### 4. Verify Security Group Created
```powershell
aws ec2 describe-security-groups --group-names water-quality-ml-sg
```

### 5. Save the Output
The script creates `aws-infrastructure-config.txt` with all important details. **Keep this file secure!**

---

## 🔐 Security Best Practices

- [ ] Never commit AWS credentials to Git
- [ ] Add `.aws/` and `*credentials*` to `.gitignore`
- [ ] Enable MFA on your AWS account
- [ ] Rotate access keys every 90 days
- [ ] Use IAM roles for EC2 instances (not access keys)
- [ ] Review CloudTrail logs periodically
- [ ] Set up billing alerts in AWS Console

---

## 💰 Cost Monitoring Setup

### Set Up Billing Alerts

1. Go to AWS Console → **Billing Dashboard**
2. Click **Budgets** → **Create budget**
3. Choose **Cost budget**
4. Set monthly budget: $50 (or your preference)
5. Set alert threshold: 80% ($40)
6. Add your email for notifications

### Enable Cost Explorer

1. AWS Console → **Cost Management**
2. Enable **Cost Explorer**
3. Review costs by service daily/weekly

---

## 🆘 Troubleshooting Common Issues

### Issue: "InvalidClientTokenId" error
**Solution:** Your AWS credentials are not configured correctly
```powershell
aws configure
# Re-enter your access keys
```

### Issue: "AccessDenied" error
**Solution:** Your IAM user lacks required permissions
- Go to IAM → Users → Your User → Add permissions
- Attach `AdministratorAccess` or required policies

### Issue: "BucketAlreadyExists" error
**Solution:** S3 bucket names must be globally unique
- The script adds a timestamp to avoid this
- If it still happens, manually edit the bucket name in the script

### Issue: "DryRunOperation" or "UnauthorizedOperation"
**Solution:** Your user doesn't have EC2 permissions
- Attach `AmazonEC2FullAccess` policy to your IAM user

### Issue: Script runs but resources not created
**Solution:** Check for error messages in the output
```powershell
# Check CloudTrail for API call failures
aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=CreateBucket
```

---

## 📞 Need Help?

- AWS Documentation: https://docs.aws.amazon.com/
- AWS Support: https://console.aws.amazon.com/support/
- Check the script output file: `aws-infrastructure-config.txt`

---

## ✨ Ready to Go!

Once all checkboxes are complete, run:

```powershell
.\infrastructure\setup-aws.ps1
```

The script will:
1. ✅ Verify your AWS credentials
2. ✅ Create S3 bucket for DVC data
3. ✅ Create ECR repository for Docker images
4. ✅ Set up IAM roles and policies
5. ✅ Create security groups
6. ✅ Generate configuration file with all details

**Estimated runtime:** 2-3 minutes

Good luck! 🚀
