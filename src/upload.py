import os
import paramiko

from celery import signals
from celery.utils.log import get_task_logger

from openrelik_worker_common.logging import Logger
from openrelik_worker_common.task_utils import create_task_result, get_input_files

from .app import celery

TASK_NAME = "openrelik-worker-sftp.tasks.upload"

TASK_METADATA = {
    "display_name": "SFTP Upload",
    "description": "Upload input files using SFTP",
    "task_config": [
        {
            "name": "host",
            "label": "Enter the hostname or IP address of the SFTP server",
            "description": "Hostname or IP address",
            "type": "text",
            "required": True,
        },
        {
            "name": "username",
            "label": "Username for authentication",
            "description": "Username",
            "type": "text",
            "required": True,
        },
        {
            "name": "password",
            "label": "Password for authentication",
            "description": "Password",
            "type": "text",
            "required": True,
        },
        {
            "name": "path",
            "label": "Path, where the files will be uploaded",
            "description": "Destination path for uploaded files",
            "type": "text",
            "required": True,
        },
    ],
}

log_root = Logger()
logger = log_root.get_logger(__name__, get_task_logger(__name__))

@signals.task_prerun.connect
def on_task_prerun(sender, task_id, task, args, kwargs, **_):
    log_root.bind(
        task_id=task_id,
        task_name=task.name,
        worker_name=TASK_METADATA.get("display_name"),
    )

@celery.task(bind=True, name=TASK_NAME, metadata=TASK_METADATA)
def command(
    self,
    pipe_result: str = None,
    input_files: list = None,
    output_path: str = None,
    workflow_id: str = None,
    task_config: dict = None,
) -> str:
    # Setup logger
    log_root.bind(workflow_id=workflow_id)
    logger.info(f"Starting {TASK_NAME} for workflow {workflow_id}")

    input_files = get_input_files(pipe_result, input_files or [])
    output_files = []
    sftp_host = task_config.get("host", None)
    sftp_username = task_config.get("username", None)
    sftp_password = task_config.get("password", None)
    upload_path = task_config.get("path", None)

    # Open an SFTP connection and upload files
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=sftp_host, port=22, username=sftp_username, password=sftp_password)
    logger.info(f"Successfully connected to {sftp_host}")
    sftp = ssh.open_sftp()
    sftp.chdir(upload_path)
    logger.info(f"Uploading files to {upload_path}")
    for file in input_files:
        file_path = file.get("path")
        destination_file_name = file.get("display_name") or os.path.basename(file_path)
        sftp.put(file_path, destination_file_name)
        logger.info(f"Successfully uploaded {destination_file_name}")
    sftp.close()
    ssh.close()
    logger.info(f"Connection to {sftp_host} closed")

    # Return
    return create_task_result(
        output_files=output_files,
        workflow_id=workflow_id,
        meta={},
    )
