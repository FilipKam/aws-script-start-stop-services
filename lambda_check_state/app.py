import boto3
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def check_rds_instance_statuses():
    rds = boto3.client("rds")
    instances = rds.describe_db_instances()["DBInstances"]
    all_available = False
    for instance in instances:
        try:
            db_instance_status = instance["DBInstanceStatus"]
            logger.info(
                f"Instance {instance['DBInstanceIdentifier']} is {db_instance_status}"
            )
            if db_instance_status == "available" or db_instance_status == "stopped":
                all_available = True
                break
        except Exception as e:
            logger.error(
                f"Error checking instance {instance['DBInstanceIdentifier']}: {e}"
            )
    return all_available


def handler(event, context):
    all_available = check_rds_instance_statuses()
    if all_available:
        status = "available"
    else:
        status = "not available"
    logger.info(f"RDS instances are {status}")
    return status
