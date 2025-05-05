from argparse import ArgumentParser
from typing import Any

from ezbatch._version import version
from ezbatch.compute_environment import (
    create_compute_environment,
    delete_compute_environment,
    list_compute_environments,
    toggle_compute_environment,
)
from ezbatch.interactive.manager import EZBatchManager
from ezbatch.job import list_jobs, submit_job
from ezbatch.job_definition import create_job_definition
from ezbatch.job_queue import (
    create_job_queue,
    delete_job_queue,
    list_job_queues,
    toggle_job_queue,
)


def sanitize_args(args: dict[str, Any]) -> dict[str, Any]:
    """Remove command, subcommand, and None values from a args dictionary."""
    del args["command"]
    del args["subcommand"]
    return {k: v for k, v in args.items() if v is not None}


def ezbatch_cli():
    """CLI function for EZBatch"""
    parser = ArgumentParser(description=f"EZBatch CLI, Version {version}")
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"EZBatch CLI, Version {version}",
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    """compute environment command"""
    compute_environment_command = subparsers.add_parser("compute-environment", help="Compute Environment Management")
    compute_environment_subcommands = compute_environment_command.add_subparsers(dest="subcommand", help="Subcommands")

    # create compute environment
    ce_create = compute_environment_subcommands.add_parser("create", help="Create a new Compute Environment")
    ce_create.add_argument("--name", type=str, required=True, help="The name of the Compute Environment")
    ce_create.add_argument("--service-role", type=str, default=None, help="The ARN of the service role")
    ce_create.add_argument(
        "--type", type=str, default="FARGATE", choices=["FARGATE", "EC2"], help="The type of the Compute Environment"
    )
    ce_create.add_argument("--max-vcpus", type=int, default=256, help="The maximum number of vCPUs")
    ce_create.add_argument("--subnets", type=str, nargs="+", default=None, help="The subnets to use")
    ce_create.add_argument(
        "--security-group-ids", type=str, nargs="+", default=None, help="The security group IDs to use"
    )
    ce_create.add_argument("--tags", type=str, nargs="+", default=[], help="The tags to apply, in the format key=value")

    # list compute environments
    compute_environment_subcommands.add_parser("list", help="List all Compute Environments")

    # toggle compute environment
    ce_toggle = compute_environment_subcommands.add_parser("toggle", help="Toggle the state of a Compute Environment")
    ce_toggle.add_argument("--name", type=str, required=True, help="The name or ARN of the Compute Environment")

    # delete compute environment
    ce_delete = compute_environment_subcommands.add_parser("delete", help="Delete a Compute Environment")
    ce_delete.add_argument("--name", type=str, required=True, help="The name or ARN of the Compute Environment")

    """job queue command"""
    job_queue_command = subparsers.add_parser("job-queue", help="Job Queue Management")
    job_queue_subcommands = job_queue_command.add_subparsers(dest="subcommand", help="Subcommands")

    # create job queue
    jq_create = job_queue_subcommands.add_parser("create", help="Create a new Job Queue")
    jq_create.add_argument("--name", type=str, required=True, help="The name of the Job Queue")
    jq_create.add_argument(
        "--compute-environment", type=str, required=True, help="The name or ARN of the Compute Environment"
    )
    jq_create.add_argument("--tags", type=str, nargs="+", default=[], help="The tags to apply, in the format key=value")

    # list job queues
    job_queue_subcommands.add_parser("list", help="List all Job Queues")

    # toggle job queue
    jq_toggle = job_queue_subcommands.add_parser("toggle", help="Toggle the state of a Job Queue")
    jq_toggle.add_argument("--name", type=str, required=True, help="The name or ARN of the Job Queue")

    # delete job queue
    jq_delete = job_queue_subcommands.add_parser("delete", help="Delete a Job Queue")
    jq_delete.add_argument("--name", type=str, required=True, help="The name or ARN of the Job Queue")

    """job definition command"""
    job_definition_command = subparsers.add_parser("job-definition", help="Job Definition Management")
    job_definition_subcommands = job_definition_command.add_subparsers(dest="subcommand", help="Subcommands")

    # create job definition
    jd_create = job_definition_subcommands.add_parser("create", help="Create a new Job Definition")
    jd_create.add_argument("--name", type=str, required=True, help="The name of the Job Definition")

    """jobs command"""
    jobs_command = subparsers.add_parser("jobs", help="Job Management")
    jobs_subcommands = jobs_command.add_subparsers(dest="subcommand", help="Subcommands")

    # submit job
    jobs_submit = jobs_subcommands.add_parser("submit", help="Submit a job to the queue")
    jobs_submit.add_argument("--name", type=str, required=True, help="The name of the job")
    jobs_submit.add_argument("--queue", type=str, required=True, help="The name or ARN of the job queue")
    jobs_submit.add_argument("--definition", type=str, required=True, help="The job definition to use")

    # list jobs
    jobs_list = jobs_subcommands.add_parser("list", help="List all jobs in the queue")
    jobs_list.add_argument("--queue", type=str, required=True, help="The name or ARN of the job queue")

    """interactive command"""
    subparsers.add_parser("interactive", help="Interactive Mode")

    # parse the arguments
    args = parser.parse_args()

    # handle the command
    if args.command == "compute-environment":
        if args.subcommand == "create":
            args_dict = vars(args)
            args_dict["tags"] = {tag.split("=")[0]: tag.split("=")[1] for tag in args_dict["tags"]}
            args_dict = sanitize_args(args_dict)
            response = create_compute_environment(**args_dict)
            print(f"Compute environment {response['computeEnvironmentName']} created.")
        elif args.subcommand == "list":
            df = list_compute_environments()
            print(df[["Name", "State", "Type", "Max vCPUs"]].to_markdown(index=False))
        elif args.subcommand == "toggle":
            response, state = toggle_compute_environment(args.name)
            print(f"Compute environment {response['computeEnvironmentName']} is now {state}")
        elif args.subcommand == "delete":
            delete_compute_environment(args.name)
            print(f"Compute environment {args.name} deleted.")
    elif args.command == "job-queue":
        if args.subcommand == "create":
            args_dict = vars(args)
            args_dict["tags"] = {tag.split("=")[0]: tag.split("=")[1] for tag in args_dict["tags"]}
            args_dict = sanitize_args(args_dict)
            response = create_job_queue(**args_dict)
            print(f"Job queue {response['jobQueueName']} created.")
        elif args.subcommand == "list":
            df = list_job_queues()
            print(df[["Name", "State", "Status", "Status Reason", "Compute Environment"]].to_markdown(index=False))
        elif args.subcommand == "toggle":
            response, state = toggle_job_queue(args.name)
            print(f"Job queue {response['jobQueueName']} is now {state}")
        elif args.subcommand == "delete":
            delete_job_queue(args.name)
            print(f"Job queue {args.name} deleted.")
    elif args.command == "jobs":
        if args.subcommand == "submit":
            args_dict = vars(args)
            args_dict = sanitize_args(args_dict)
            response = submit_job(**args_dict)
            print(f"Job {response['jobName']} submitted to queue {args.queue} with definition {args.definition}")
        elif args.subcommand == "list":
            list_jobs(args.queue)
    elif args.command == "interactive":
        app = EZBatchManager()
        app.run()
