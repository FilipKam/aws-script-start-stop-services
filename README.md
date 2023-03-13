# ABOUT

This tool set is used to automatically start and stop AWS resources. It is designed to be used in AWS Lambda function. Automation is done using Step Functions. RDS, EC2 and ECS resources will be started and stopped.

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

## MANUAL USAGE OF MANAGE SERVICES LAMBDA FUNCTION

- Create lambda function manually or deploy whole solution with CloudFormation (description above)
- Lambda must have permissions to start, stop, list and describe (check IAM role described in lambda_functions.yaml):
  - EC2
  - ECS
  - RDS
- Lambda can be controlled using testing lambda event input JSON
  - Start RDS: ```{"action": "start", "resource": "rds"}```
  - Start ECS: ```{"action": "start", "resource": "ecs"}```
  - Stop all: ```{"action": "stop"}```

## LOCAL USAGE OF MANAGE SERVICES SCRIPT

### START RESOURCES

```python3 app.py -a start -r rds```

```python3 app.py -a start -r ecs```

### STOP RESOURCES

```python3 app.py -a stop```
