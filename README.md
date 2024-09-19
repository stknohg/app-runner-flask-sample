# Sample Flask application for AWS App Runner

* [For PowerShell user](./README_PowerShell.md)
* [For Nushell user](./README_Nushell.md)

If you only need the result, run the following commands in AWS CloudShell with Docker support.

* [AWS CloudShell : Supported Regions for Docker](https://docs.aws.amazon.com/cloudshell/latest/userguide/supported-aws-regions.html#docker-regions)

```bash
#
# Start AWS CloudShell
#

# 1. Create ECR repository
aws ecr create-repository --repository-name 'my-flask-app'

# 2. Create docker image
git clone https://github.com/stknohg/app-runner-flask-sample.git --depth 1
cd ./app-runner-flask-sample/
docker build -t my-flask-app .

# 3. Push docker image to ECR
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
aws ecr get-login-password | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
docker tag my-flask-app:latest "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/my-flask-app:latest"
docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/my-flask-app:latest"

# 4. Create App Runner service
aws cloudformation create-stack --stack-name my-flask-app --template-body file://./app-runner.yaml --capabilities CAPABILITY_NAMED_IAM
```

## How to start local server

```bash
# Bash
export FLASK_APP="./app/app.py"
export AWS_PROFILE="<your AWS profile>"
export POSTGRES_URL="<your PostgreSQL connection URL>"
flask run --host=0.0.0.0 --port=5000 --debug
```

## How to create docker image

```bash
# Bash
docker build -t my-flask-app .
```

### (optional) Run docker container localy

```bash
# Bash
docker run -it -p 5000:5000 --rm my-flask-app
```

## How to push docker image to ECR repository

### Create ECR Repository (AWS CLI)

```bash
# Bash
export AWS_PROFILE="<your AWS profile>"
aws ecr create-repository --repository-name 'my-flask-app'
```

### Push docker image to ECR

```bash
# Bash
export AWS_PROFILE="<your AWS profile>"
accountId=$(aws sts get-caller-identity --query 'Account' --output text)
region=$(aws ec2 describe-availability-zones --output text --query 'AvailabilityZones[0].[RegionName]')

# docker login
aws ecr get-login-password --region $region | docker login --username AWS --password-stdin "$accountId.dkr.ecr.$region.amazonaws.com"
# docker tag and push
docker tag my-flask-app:latest "$accountId.dkr.ecr.$region.amazonaws.com/my-flask-app:latest"
docker push "$accountId.dkr.ecr.$region.amazonaws.com/my-flask-app:latest"
```

## How to create App Runner Service

Use CloudFormation stack [app-runner.yaml](./app-runner.yaml).

```bash
# Bash 
export AWS_PROFILE="<your AWS profile>"
aws cloudformation create-stack --stack-name my-flask-app \
    --template-body file://./app-runner.yaml \
    --capabilities CAPABILITY_NAMED_IAM
```

### Start App Runner Deployment

```bash
# Bash
export service_name='my-flask-app'
service_arn=$(aws apprunner list-services --query "ServiceSummaryList[?ServiceName==\`$service_name\`].ServiceArn" --output text)
aws apprunner start-deployment --service-arn $service_arn
```
