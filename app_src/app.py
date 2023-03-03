import boto3
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class AWSManager:
    def __init__(self):
        # create clients for EC2, ECS and RDS
        self.ec2_client = boto3.client("ec2")
        self.ecs_client = boto3.client("ecs")
        self.rds_client = boto3.client("rds")

    def start_ec2_instances(self):
        # start all EC2 instances
        try:
            response = self.ec2_client.describe_instances()
            if response["Reservations"]:
                for reservation in response["Reservations"]:
                    for instance in reservation["Instances"]:
                        instance_id = instance["InstanceId"]
                        self.ec2_client.start_instances(InstanceIds=[instance_id])
                        logger.info(f"Started EC2 instance {instance_id}")
            else:
                raise Exception("No EC2 instances found.")
        except Exception as e:
            logger.error(e)

    def stop_ec2_instances(self):
        # stop all EC2 instances
        try:
            response = self.ec2_client.describe_instances()
            if response["Reservations"]:
                for reservation in response["Reservations"]:
                    for instance in reservation["Instances"]:
                        instance_id = instance["InstanceId"]
                        self.ec2_client.stop_instances(InstanceIds=[instance_id])
                        logger.info(f"Stopped EC2 instance {instance_id}")
            else:
                raise Exception("No EC2 instances found.")
        except Exception as e:
            logger.error(e)

    def start_rds_db(self):
        # start all RDS instances
        try:
            response = self.rds_client.describe_db_instances()
            if response["DBInstances"]:
                for db_instance in response["DBInstances"]:
                    db_instance_id = db_instance["DBInstanceIdentifier"]
                    try:
                        self.rds_client.start_db_instance(
                            DBInstanceIdentifier=db_instance_id
                        )
                        logger.info(f"Started RDS instance {db_instance_id}")
                    except ClientError as e:
                        if e.response["Error"]["Code"] == "InvalidDBInstanceState":
                            logger.error(
                                f"RDS instance {db_instance_id} cannot be started as it is not in a valid state"
                            )
                        else:
                            raise
            else:
                raise Exception("No RDS instances found.")
        except Exception as e:
            logger.error(e)

    def stop_rds_db(self):
        # stop all RDS instances
        try:
            response = self.rds_client.describe_db_instances()
            if response["DBInstances"]:
                for db_instance in response["DBInstances"]:
                    db_instance_id = db_instance["DBInstanceIdentifier"]
                    try:
                        self.rds_client.stop_db_instance(
                            DBInstanceIdentifier=db_instance_id
                        )
                        logger.info(f"Stopped RDS instance {db_instance_id}")
                    except ClientError as e:
                        if e.response["Error"]["Code"] == "InvalidDBInstanceState":
                            logger.error(
                                f"RDS instance {db_instance_id} cannot be stopped as it is not in a valid state"
                            )
                        else:
                            raise
            else:
                raise Exception("No RDS instances found.")
        except Exception as e:
            logger.error(e)

    def ecs_change_desired_tasks(self, desired_count):
        # edit number of desired ECS tasks
        try:
            clusters = self.ecs_client.list_clusters()
            cluster_arns = clusters["clusterArns"]
            for cluster_arn in cluster_arns:
                cluster_info = self.ecs_client.describe_clusters(
                    clusters=[cluster_arn]
                )["clusters"][0]
                if cluster_info["status"] == "ACTIVE":
                    cluster_name = cluster_info["clusterName"]
                    logger.info(
                        f"Updating number of service tasks to {desired_count} in {cluster_name}"
                    )
                    services = self.ecs_client.list_services(cluster=cluster_name)
                    services_arns = services["serviceArns"]
                    for service_arn in services_arns:
                        self.ecs_client.update_service(
                            cluster=cluster_name,
                            service=service_arn,
                            desiredCount=desired_count,
                        )
                        logger.info(
                            f"Desired number of tasks changed to {desired_count} for {service_arn}"
                        )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ClusterNotFoundException":
                logger.error("No ECS clusters present, nothing to stop")
            elif e.response["Error"]["Code"] == "AccessDeniedException":
                logger.error("Access denied to ECS, check your credentials")
            else:
                logger.error(f"An error occurred while stopping ECS tasks: {e}")


def handler(event, context):
    """
    Main function that is executed when the script is triggered
    """
    # create an instance of the AWSManager class
    manager = AWSManager()
    # get the action from the event
    action = event["action"]
    if action == "start":
        logger.info("Starting all AWS resources")
        # manager.start_ec2_instances()
        manager.start_rds_db()
        manager.ecs_change_desired_tasks(desired_count=1)
        return {"statusCode": 200, "body": "All resources started"}
    elif action == "stop":
        logger.info("Stopping all AWS resources")
        manager.stop_ec2_instances()
        manager.ecs_change_desired_tasks(desired_count=0)
        manager.stop_rds_db()
        return {"statusCode": 200, "body": "All resources stopped"}


if __name__ == "__main__":
    logging.info("Script started from local machine")
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", help="stop or start", type=str)
    args = parser.parse_args()
    event = {"action": args.action}
    handler(event, None)
