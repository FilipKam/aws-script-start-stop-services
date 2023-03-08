# ABOUT

Script running in lambda functions for starting/stopping EC2, ECS and RDS resources.

## HOW TO USE SCRIPT IN LAMBDA FUNCTION

- Create lambda function manually or using CloudFormation script infra.yaml
- Lambda must have permissions to start, stop, list and describe:
  - EC2
  - ECS
  - RDS
- For testing lambda event input JSON is defined like:

### Start RDS instances

```
{
  "action": "start",
  "resource": "rds"
}
```

### Start ECS tasks

```
{
  "action": "start",
  "resource": "ecs"
}
```

### Stop all resources

```
{
  "action": "stop"
}
```

## HOW TO USE SCRIPT LOCALLY

### start resources

```python3 app.py -a start -r rds```

```python3 app.py -a start -r ecs```

### stop resources

```python3 app.py -a stop```
