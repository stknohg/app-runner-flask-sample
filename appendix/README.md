# Appendix

## ECS Express Mode template (ecs-express.yaml)

We provide an ECS Express Mode template for comparison with App Runner.  
After pushing the Docker Image to ECR, run the `ecs-express.yaml` template.  

```bash
#
# Start AWS CloudShell
#

# Create a default VPC if one does not exist.
aws ec2 create-default-vpc 

# Create ECS Express Mode cluster and service.
aws cloudformation create-stack --stack-name my-flask-app-express --template-body file://./ecs-express.yaml --capabilities CAPABILITY_NAMED_IAM
```

To enable ECS Exec, run the following command and restart the task.

```bash
# Enable ECS Exec
aws ecs update-service --cluster my-cluster-express --service my-flask-app-express --enable-execute-command
```

## Lambda Web Adapter template (template.yaml)

We provide an Lambda Web Adapter template for comparison with App Runner.  
Use AWS SAM CLI with `template.yaml` template.  

This template is based on [AWS Lambda Web Adapter](https://github.com/awslabs/aws-lambda-web-adapter).  

```bash
#
# Start AWS CloudShell
#
sam build
sam deploy --guided
```
