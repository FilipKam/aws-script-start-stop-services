import logging
from lib.aws import AWSManager


def handler(event, context):
    """
    Main function that is executed when the script is triggered
    """

    # set up logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # create an instance of the AWSManager class
    aws_manager = AWSManager(logger)
    # get the action from the event
    action = event["action"]

    if action == "start":
        resources = event.get("resources", [])
        if not resources:
            return {"statusCode": 400, "body": "No resources provided"}

        response_body = []
        for resource in resources:
            if resource == "rds":
                logger.info("Starting all RDS instances")
                aws_manager.start_rds_db()
                response_body.append("All RDS instances started")
            elif resource == "ecs":
                logger.info("Setting up ECS tasks to 1")
                aws_manager.ecs_change_desired_tasks(desired_count=1)
                response_body.append("Desired number of ECS tasks set to 1")
            elif resource == "asg":
                logger.info("Setting up ASG instances to 1")
                aws_manager.ec2_asg_desired_capacity(desired_count=1)
                response_body.append("Desired number of ASG instances set to 1")
            else:
                logger.warning(f"Unsupported resource {resource}")

        return {"statusCode": 200, "body": response_body}

    elif action == "stop":
        logger.info("Stopping all AWS resources")
        aws_manager.stop_ec2_instances()
        aws_manager.stop_rds_db()
        aws_manager.ecs_change_desired_tasks(desired_count=0)
        aws_manager.ec2_asg_desired_capacity(desired_count=0)
        return {"statusCode": 200, "body": "All resources stopped"}

    else:
        return {"statusCode": 400, "body": "Invalid action provided"}


if __name__ == "__main__":
    logging.info("Script started from local machine")
    import argparse

    class CommaSeparatedListAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, values.split(","))

    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", help="stop or start", type=str)
    parser.add_argument(
        "-r",
        "--resources",
        help="rds, ecs, asg",
        type=str,
        action=CommaSeparatedListAction,
    )
    args = parser.parse_args()
    event = {"action": args.action, "resources": args.resource}

    handler(event, None)
