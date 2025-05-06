"""GCP-specific deployment functionality."""

import json
import os
import subprocess
import tempfile

from dayhoff_tools.deployment.deploy_utils import get_container_env_vars


def check_job_exists(job_name: str, region: str) -> bool:
    """Check if a job with the given name already exists in GCP Batch.

    Args:
        job_name: Name of the job to check
        region: GCP region to check in

    Returns:
        bool: True if the job exists, False otherwise

    Note:
        This uses gcloud batch jobs describe, which will return a non-zero
        exit code if the job doesn't exist.
    """
    try:
        subprocess.run(
            [
                "gcloud",
                "batch",
                "jobs",
                "describe",
                job_name,
                "--location",
                region,
            ],
            check=True,
            capture_output=True,  # Suppress output
        )
        return True
    except subprocess.CalledProcessError:
        return False


def create_batch_job_config(config: dict, image_uri: str) -> dict:
    """Create a GCP Batch job configuration from YAML config.

    Args:
        config: Dictionary containing the configuration loaded from YAML
        image_uri: URI of the Docker image to use

    Returns:
        Dictionary containing GCP Batch job configuration
    """
    gcp_config = config["gcp"]

    # Start with the allocation and logs policies
    batch_config = {
        "allocationPolicy": gcp_config["allocation_policy"],
        "logsPolicy": gcp_config["logs_policy"],
    }

    entrypoint_command = config["docker"].get("container_entrypoint")
    if entrypoint_command is None:
        raise ValueError("docker.container_entrypoint is required in configuration")

    if not isinstance(entrypoint_command, list) or not all(
        isinstance(x, str) for x in entrypoint_command
    ):
        raise ValueError("docker.container_entrypoint must be a list of strings")

    # Build the container configuration with bash entrypoint
    container_config = {
        "imageUri": image_uri,
        "entrypoint": "/bin/bash",
        "commands": ["-c", " ".join(entrypoint_command)],
    }

    # Add shared memory option if specified
    if "shared_memory" in config.get("docker", {}):
        container_config["options"] = f"--shm-size={config['docker']['shared_memory']}"

    # Build the task group configuration
    task_group = {
        "taskCount": gcp_config["batch_job"]["taskCount"],
        "parallelism": gcp_config["batch_job"]["parallelism"],
        "taskSpec": {
            "computeResource": gcp_config["batch_job"]["computeResource"],
            "runnables": [{"container": container_config}],
        },
    }

    # Get all environment variables, including special ones like WANDB_API_KEY and GCP credentials
    env_vars = get_container_env_vars(config)

    # Add environment variables if any exist
    if env_vars:
        task_group["taskSpec"]["runnables"][0]["environment"] = {"variables": env_vars}

    # Add machine type and optional accelerators from instance config
    instance_config = gcp_config["batch_job"]["instance"]
    if "machineType" in instance_config:
        # Add machine type to the allocation policy
        if "policy" not in batch_config["allocationPolicy"]["instances"]:
            batch_config["allocationPolicy"]["instances"]["policy"] = {}
        batch_config["allocationPolicy"]["instances"]["policy"]["machineType"] = (
            instance_config["machineType"]
        )

    # Add accelerators if present (optional)
    if "accelerators" in instance_config:
        batch_config["allocationPolicy"]["instances"]["policy"]["accelerators"] = (
            instance_config["accelerators"]
        )

    # Add the task group to the configuration
    batch_config["taskGroups"] = [task_group]

    # Debug logging to verify configuration
    print("\nGCP Batch Configuration:")
    print("------------------------")
    try:
        policy = batch_config["allocationPolicy"]["instances"]["policy"]
        print("Machine Type:", policy.get("machineType", "Not specified"))
        print("Accelerators:", policy.get("accelerators", "Not specified"))
        print("Environment Variables:", list(env_vars.keys()))
    except KeyError as e:
        print(f"Warning: Could not find {e} in configuration")

    return batch_config


def submit_gcp_batch_job(config: dict, image_uri: str) -> None:
    """Submit a job to GCP Batch.

    Args:
        config: Dictionary containing the configuration loaded from YAML
        image_uri: URI of the Docker image to use

    Raises:
        ValueError: If a job with the same name already exists
    """
    job_name = config["gcp"]["job_name"]
    region = config["gcp"]["region"]

    # Check if job already exists
    if check_job_exists(job_name, region):
        raise ValueError(
            f"Job '{job_name}' already exists in region {region}. "
            "Please choose a different job name or delete the existing job first."
        )

    # Create GCP Batch job configuration
    batch_config = create_batch_job_config(config, image_uri)

    # Write the configuration to a temporary file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        json.dump(batch_config, temp_file, indent=2)
        temp_config_path = temp_file.name

    try:
        # Submit the job using gcloud
        command = [
            "gcloud",
            "batch",
            "jobs",
            "submit",
            job_name,
            "--location",
            region,
            "--config",
            temp_config_path,
        ]
        subprocess.run(command, check=True)
    finally:
        # Clean up the temporary file
        os.unlink(temp_config_path)
