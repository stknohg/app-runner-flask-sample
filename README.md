# Sample Flask application for AWS App Runner

## How to start local server

```powershell
# for PowerShell 
$env:FLASK_APP="./app/app.py"
$env:AWS_PROFILE="<your AWS profile>"
$env:POSTGRES_URL="<your PostgreSQL connection URL>"
flask run --host=0.0.0.0 --port=5000 --debug
```

## How to create docker image

```powershell
docker build -t my-flask-app .
```

### (optional) Run docker container localy

```powershell
docker run -it -p 5000:5000 --rm my-flask-app
```

## How to push docker image to ECR repository

* Create ECR Repository (AWS CLI)

```powershell
# for PowerShell
$env:AWS_PROFILE="<your AWS profile>"
aws ecr create-repository --repository-name my-flask-app
```

* Push docker image to ECR

```powershell
# for PowerShell
$env:AWS_PROFILE="<your AWS profile>"
$accountId = aws sts get-caller-identity --query "Account" --output text
$region = aws ec2 describe-availability-zones --output text --query 'AvailabilityZones[0].[RegionName]'

# docker login
aws ecr get-login-password --region $region | docker login --username AWS --password-stdin "$accountId.dkr.ecr.$region.amazonaws.com"

# docker tag
docker tag my-flask-app:latest "$accountId.dkr.ecr.$region.amazonaws.com/my-flask-app:latest"

# docker push
docker push "$accountId.dkr.ecr.$region.amazonaws.com/my-flask-app:latest"
```

# How to create App Runner Service

```powershell
# for PowerShell
$env:AWS_PROFILE="<your AWS profile>"
$accountId = aws sts get-caller-identity --query "Account" --output text
$region = aws ec2 describe-availability-zones --output text --query 'AvailabilityZones[0].[RegionName]'

# Define utility filter to escape JSON
filter EscapeJson {
    if ($PSNativeCommandArgumentPassing -in ('Windows', 'Standard')) {
        return $_
    }
    return $_ -replace '"','\"'
}

# Create IAM Role for ECR access
$policyDocument = @"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "build.apprunner.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
"@ | EscapeJson
aws iam create-role --role-name 'AppRunnerECRAccessRole' --path '/service-role/' --assume-role-policy-document $policyDocument
aws iam attach-role-policy --role-name 'AppRunnerECRAccessRole' --policy-arn 'arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess'

# Create IAM Role for DynamoDB access
$policyDocument = @"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "tasks.apprunner.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
"@ | EscapeJson
aws iam create-role --role-name 'my-flask-app-task-role' --assume-role-policy-document $policyDocument
$inlinePolicy = @"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DynamoDB",
      "Effect": "Allow",
      "Action": [
        "dynamodb:BatchGetItem",
        "dynamodb:GetShardIterator",
        "dynamodb:GetItem",
        "dynamodb:Scan",
        "dynamodb:Query",
        "dynamodb:GetRecords"
      ],
      "Resource": "arn:aws:dynamodb:${region}:${accountId}:table/Employee"
    }
  ]
}
"@ | EscapeJson
aws iam put-role-policy --role-name 'my-flask-app-task-role' --policy-name 'my-flask-app-task-policy' --policy-document $inlinePolicy

# Create App Runner service (exclude PostgreSQL and DynamoDB configurations)
$serviceName = 'my-flask-app'
$params = @"
{
  "ServiceName": "${serviceName}",
  "SourceConfiguration": {
    "AuthenticationConfiguration": {
      "AccessRoleArn": "arn:aws:iam::${accountId}:role/service-role/AppRunnerECRAccessRole"
    },
    "ImageRepository": {
        "ImageIdentifier": "$accountId.dkr.ecr.$region.amazonaws.com/my-flask-app:latest",
        "ImageConfiguration": {
          "Port": "5000",
          "RuntimeEnvironmentVariables": {
              "POSTGRES_URL": "postgresql://postgres:password@localhost:5432/postgres"
          }
        },
        "ImageRepositoryType": "ECR"
    },
    "AutoDeploymentsEnabled": false
  },
  "InstanceConfiguration": {
    "Cpu": "0.25 vCPU",
    "Memory": "0.5 GB",
    "InstanceRoleArn": "arn:aws:iam::${accountId}:role/my-flask-app-task-role"
  }
}
"@ | EscapeJson
aws apprunner create-service --cli-input-json $params

# Start deployment
$serviceArn = aws apprunner list-services --query "ServiceSummaryList[?ServiceName==``${serviceName}``].ServiceArn" --output text
aws apprunner start-deployment --service-arn $serviceArn
```