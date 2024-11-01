# [Nushell] Development

* [For Bash user](./DEVELOPMENT.md)

> [!NOTE]
> Tested on Nushell 0.99.1.

## How to upgrade requirements

```powershell
# Nushell
uv pip compile ./app/requirements.in -o ./app/requirements.txt --upgrade
uv pip sync ./app/requirements.txt
```

## How to start local server

```powershell
# Nushell
$env.FLASK_APP = "./app/app.py"
$env.AWS_PROFILE = "<your AWS profile>"
$env.POSTGRES_URL = "<your PostgreSQL connection URL>"
flask run --host=0.0.0.0 --port=5000 --debug
```

## How to create docker image

```powershell
# Nushell
docker build -t my-flask-app .
```

### (optional) Run docker container localy

```powershell
# Nushell
docker run -it -p 5000:5000 --rm my-flask-app
```

## How to push docker image to ECR repository

### Create ECR Repository (AWS CLI)

```powershell
# Nushell
$env.AWS_PROFILE = "<your AWS profile>"
aws ecr create-repository --repository-name 'my-flask-app'
```

### Push docker image to ECR

```powershell
# Nushell 
$env:AWS_PROFILE = "<your AWS profile>"
let accountId = aws sts get-caller-identity --query 'Account' --output text
let region = aws ec2 describe-availability-zones --output text --query 'AvailabilityZones[0].[RegionName]'

# docker login
aws ecr get-login-password --region $region | docker login --username AWS --password-stdin $"($accountId).dkr.ecr.($region).amazonaws.com"
# docker tag and push
docker tag my-flask-app:latest $"($accountId).dkr.ecr.($region).amazonaws.com/my-flask-app:latest"
docker push $"($accountId).dkr.ecr.($region).amazonaws.com/my-flask-app:latest"
```

## How to create App Runner Service

Use CloudFormation stack [app-runner.yaml](./app-runner.yaml).

```powershell
# Nushell 
$env.AWS_PROFILE = "<your AWS profile>"
(aws cloudformation create-stack --stack-name my-flask-app
    --template-body file://./app-runner.yaml
    --capabilities CAPABILITY_NAMED_IAM )
```

### Start App Runner Deployment

```powershell
# Nushell
let serviceName = 'my-flask-app'
let serviceArn = aws apprunner list-services --query $"ServiceSummaryList[?ServiceName==`($serviceName)`].ServiceArn" --output text
aws apprunner start-deployment --service-arn $serviceArn
```
