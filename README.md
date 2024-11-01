# Sample Flask application for AWS App Runner

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
