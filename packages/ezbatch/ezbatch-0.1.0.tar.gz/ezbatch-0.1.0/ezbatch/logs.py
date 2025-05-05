from .client import LOGS_CLIENT


def get_task_log(task_id: str):
    """Get the log of a task.

    Parameters
    ----------
    task_id : str
        The task ID.
    """
    log_stream_name = f"test-job-definition-2/container1/2e7dab38f600403b9df0b6d2c4ef1062"
    log_events = LOGS_CLIENT.get_log_events(logGroupName="/aws/batch/job", logStreamName=log_stream_name)
    return log_events
