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
                desired_count = event.get("config", {}).get("ecs", {}).get("desired_count") or 1
                logger.info(f"Setting up ECS tasks to {desired_count}")
                aws_manager.ecs_change_desired_tasks(desired_count=int(desired_count))
                response_body.append(f"Desired number of ECS tasks set to {desired_count}")
            elif resource == "asg":
                desired_count = event.get("config", {}).get("asg", {}).get("desired_count") or 1
                logger.info(f"Setting up ASG instances to {desired_count}")
                aws_manager.ec2_asg_desired_capacity(desired_count=int(desired_count))
                response_body.append(f"Desired number of ASG instances set to {desired_count}")
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
    parser.add_argument("-asgc", "--asg_count", help="ASG desired count", type=int)
    parser.add_argument("-ecsc", "--ecs_count", help="ECS desired count", type=int)
    args = parser.parse_args()
    event = {
        "action": args.action,
        "resources": args.resources,
        "config": {
            "asg": {
                "desired_count": args.asg_count
            },
            "ecs": {
                "desired_count": args.ecs_count
            }
        },
    }
    handler(event, None)
