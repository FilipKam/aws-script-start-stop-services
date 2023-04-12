# START AND STOP AWS RESOURCES SCRIPT

## DESCRIPTION

This tool set is used to automatically start and stop AWS resources. It is designed to be used in AWS Lambda function. Automation is done using Step Functions. RDS, EC2 and ECS resources will be started and stopped.

### SUPPORTED AWS RESOURCES

- RDS - Relational Database Service
- ASG - Auto Scaling Group
- ECS - Elastic Container Service
- EC2 - Elastic Compute Cloud

## DEPLOYMENT

### PREREQUISITES

- AWS account
- S3 bucket

### DEPLOYMENT STEPS

- Clone this repository to your local machine
- Upload all files to prepared S3 bucket
- Go to AWS CloudFormation console
- Click on "Create stack"
  - **Step 1 Create stack**
    - Select "Template is ready"
    - Select "Amazon S3 URL"
      - In the "Amazon S3 URL" field enter the Object URL of the template file "infra.yaml" in your S3 bucket
  - **Step 2 Specify stack details**
    - Enter stack name
      - Example: "services-manager-stack"
    - Enter NamePrefix
      - Example: "services-manager"
    - Select "Environment"
    - Enter S3 bucket name
    - Enter S3 Key for LambdaManageServicesSourceCode
    - Enter Object URL for LambdaFunctionsTemplateUrl
    - Enter Object URL for StepFunctionsTemplateUrl
  - **Step 3 Configure stack options**
    - Leave default values
  - **Step 4 Review**
    - Check all parameters
    - Tick "I acknowledge that AWS CloudFormation might create IAM resources"
    - Tick "I acknowledge that AWS CloudFormation might require the following capability: CAPABILITY_AUTO_EXPAND"
    - Click on "Submit"
- Verify that all resources are created
- Resources will be now automatically started and stopped according to schedule specified in EventBridge Schedule

## USAGE

### STEP FUNCTIONS

- step_functions.yaml contains Step Functions definition
- it is used to control start and stop of resources according to schedule specified in EventBridge Schedule
- Schedule can be changed using cron expression which is specified in the infra.yaml file as a parameter

### MANUAL USAGE OF MANAGE SERVICES LAMBDA FUNCTION

- Create lambda function manually or deploy whole solution with CloudFormation (description above)
- Lambda must have permissions to start, stop, list and describe (check IAM role described in lambda_functions.yaml):
  - EC2
  - ECS
  - RDS
- Lambda can be controlled using testing lambda event input JSON
  - Start single resource: ```{ "action": "start", "resources": [ "ecs" ] }```
  - Start all resources: ```{ "action": "start", "resources": [ "ecs", "rds", "asg", "ec2" ] }```
  - Stop all: ```{"action": "stop"}```

### LOCAL USAGE OF MANAGE SERVICES SCRIPT

#### START RESOURCES

Multiple resources at once using comma separated list without space after comma.

- ```python3 app.py -a start -r rds,asg```

Only one resource at once using single resource name.

- ```python3 app.py -a start -r ecs```

#### STOP RESOURCES

Stop all resources always.

```python3 app.py -a stop```
