import boto3
import logging
from botocore.exceptions import ClientError


class AWSManager:
    def __init__(self, logger: logging.Logger):
        # create clients for EC2, ECS and RDS
        self.ec2_client = boto3.client("ec2")
        self.ecs_client = boto3.client("ecs")
        self.rds_client = boto3.client("rds")
        self.asg_client = boto3.client("autoscaling")
        self.logger = logger

    def start_ec2_instances(self) -> None:
        # start all EC2 instances
        try:
            response = self.ec2_client.describe_instances()
            if response["Reservations"]:
                for reservation in response["Reservations"]:
                    for instance in reservation["Instances"]:
                        instance_id = instance["InstanceId"]
                        self.ec2_client.start_instances(InstanceIds=[instance_id])
                        self.logger.info(f"Started EC2 instance {instance_id}")
            else:
                raise Exception("No EC2 instances found.")
        except Exception as e:
            self.logger.error(e)

    def stop_ec2_instances(self) -> None:
        # stop all EC2 instances
        try:
            response = self.ec2_client.describe_instances()
            if response["Reservations"]:
                for reservation in response["Reservations"]:
                    for instance in reservation["Instances"]:
                        instance_id = instance["InstanceId"]
                        self.ec2_client.stop_instances(InstanceIds=[instance_id])
                        self.logger.info(f"Stopped EC2 instance {instance_id}")
            else:
                raise Exception("No EC2 instances found.")
        except Exception as e:
            self.logger.error(e)

    def start_rds_db(self) -> None:
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
                        self.logger.info(f"Started RDS instance {db_instance_id}")
                    except ClientError as e:
                        if e.response["Error"]["Code"] == "InvalidDBInstanceState":
                            self.logger.error(
                                f"RDS instance {db_instance_id} cannot be started as it is not in a valid state"
                            )
                        else:
                            raise
            else:
                raise Exception("No RDS instances found.")
        except Exception as e:
            self.logger.error(e)

    def stop_rds_db(self) -> None:
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
                        self.logger.info(f"Stopped RDS instance {db_instance_id}")
                    except ClientError as e:
                        if e.response["Error"]["Code"] == "InvalidDBInstanceState":
                            self.logger.error(
                                f"RDS instance {db_instance_id} cannot be stopped as it is not in a valid state"
                            )
                        else:
                            raise
            else:
                raise Exception("No RDS instances found.")
        except Exception as e:
            self.logger.error(e)

    def ecs_change_desired_tasks(self, desired_count: int) -> None:
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
                    self.logger.info(
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
                        self.logger.info(
                            f"Desired number of tasks changed to {desired_count} for {service_arn}"
                        )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ClusterNotFoundException":
                self.logger.error("No ECS clusters present, nothing to stop")
            elif e.response["Error"]["Code"] == "AccessDeniedException":
                self.logger.error("Access denied to ECS, check your credentials")
            else:
                self.logger.error(f"An error occurred while stopping ECS tasks: {e}")

    def ec2_asg_desired_capacity(self, desired_count: int) -> None:
        try:
            # Get a list of all the auto scaling groups in the region
            asg_response = self.asg_client.describe_auto_scaling_groups()
        except Exception as e:
            # Log and raise the error
            self.logger.error(
                f"Error occurred while retrieving Auto Scaling Groups: {e}"
            )
            raise e

        # Loop through each auto scaling group and set the capacity
        for asg in asg_response["AutoScalingGroups"]:
            # Get the current capacity of the auto scaling group
            current_capacity = asg["DesiredCapacity"]

            try:
                # Set the minimum, maximum and desired capacity of the auto scaling group
                self.asg_client.update_auto_scaling_group(
                    AutoScalingGroupName=asg["AutoScalingGroupName"],
                    MinSize=desired_count,
                    MaxSize=desired_count,
                    DesiredCapacity=desired_count,
                )
            except Exception as e:
                self.logger.error(
                    f"Error occurred while updating Auto Scaling Group {asg['AutoScalingGroupName']}: {e}"
                )
                raise e

            self.logger.info(
                f"Capacity updated for Auto Scaling Group {asg['AutoScalingGroupName']}: from {current_capacity} to {desired_count}"
            )
