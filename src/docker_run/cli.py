#!/bin/env python3
import subprocess
import argparse
import yaml
import sys
import glob
import os

def run_command(command, ignore_errors=False):
    """
    Executes a shell command.
    """
    try:
        subprocess.run(command, check=True, shell=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        if not ignore_errors:
            # Print stderr to provide feedback on what went wrong
            print(f"An error occurred: {e.stderr.decode().strip()}")
        return False


def resource_exists(resource_type, name):
    """
    Checks if a specified Docker network or volume exists.

    Args:
        resource_type (str): Type of the resource ('network' or 'volume').
        name (str): The name of the resource to check.

    Returns:
        bool: True if the resource exists, False otherwise.
    """
    command = f"docker {resource_type} ls --format '{{{{.Name}}}}' | grep -w {name}"
    # Using run_command function with ignore_errors=True, because grep will exit with 1 if no lines match
    return run_command(command, ignore_errors=True)


def create_resource_if_missing(resource_type, name):
    """
    Creates a Docker network or volume if it does not already exist.

    Args:
        resource_type (str): Type of the resource ('network' or 'volume').
        name (str): The name of the resource.
    """
    if not resource_exists(resource_type, name):
        if not run_command(f"docker {resource_type} create {name}"):
            print(f"Failed to create {resource_type} '{name}'.")
            sys.exit(1)

def get_config_path(config_name):
    """Constructs the file path for the given configuration name."""
    home_dir = os.environ.get("HOME")
    config_dir = os.path.join(home_dir, ".config", "docker-run")
    matches = glob.glob(os.path.join(config_dir, f"{config_name}.yml")) + glob.glob(os.path.join(config_dir, f"{config_name}.yaml"))

    if len(matches) == 0:
        print(f"No configuration file found for {config_name} in {config_dir}.")
        sys.exit(1)
    elif len(matches) > 1:
        print(f"Multiple configuration files found for {config_name} in {config_dir}: {', '.join(matches)}")
        sys.exit(1)
        
    config_path = os.path.join(home_dir, ".config", "docker-run", f"{config_name}.yaml")
    if not os.path.exists(config_path):
        print(f"Configuration file not found: {config_path}")
        sys.exit(1)
    return config_path


def main():
    """
    Main function to process the YAML config and manage Docker resources.
    """
    parser = argparse.ArgumentParser(description="Manage Docker containers based on YAML configurations.")
    parser.add_argument("config_name", help="Name of the configuration file (without extension).")
    args = parser.parse_args()

    config_path = get_config_path(args.config_name)
        
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
    except Exception as e:
        print(f"Failed to load YAML configuration: {e}")
        sys.exit(1)

    # Create networks and volumes as needed
    for network_name in config.get("networks", {}):
        create_resource_if_missing("network", network_name)

    for volume_name in config.get("volumes", {}):
        create_resource_if_missing("volume", volume_name)

    container_config = config.get("container", {})
    image = container_config.get("image")
    container_name = container_config.get("name")
    network = container_config.get("network")

    # Construct volume, port, and environment variable mappings
    volume_mapping = " ".join(
        f"-v {host_path}:{container_path}"
        for volume in container_config.get("volume", [])
        for host_path, container_path in volume.items()
    )
    port_mapping = " ".join(f"-p {p}" for p in container_config.get("ports", []))
    environment_vars_string = " ".join(
        f"-e {key}='{value}'"
        for env_var in container_config.get("environment", [])
        for key, value in env_var.items()
    )

    docker_run_command = (
        f"docker run -d --network {network} --name {container_name} "
        f"{volume_mapping} {port_mapping} {environment_vars_string} {image}"
    )

    if not run_command(docker_run_command):
        print(f"Failed to run container '{container_name}'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
