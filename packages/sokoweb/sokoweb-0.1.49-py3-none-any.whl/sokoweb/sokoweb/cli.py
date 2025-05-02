# File: cli.py
import os
import subprocess
import sys
import shutil
import tempfile
import re
from pathlib import Path
from importlib import resources  # Python 3.9+

SOKOWEB_TEMPFILE_NAME = ".sokoweb_temp_dir"

def read_existing_env(env_path):
    existing_vars = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    existing_vars[key.strip()] = value.strip()
    return existing_vars

def validate_port(port):
    try:
        p_int = int(port)
        return 1024 <= p_int <= 65535
    except ValueError:
        return False

def validate_hostname(hostname):
    if not hostname:
        return False
    ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}|[a-zA-Z0-9\.-]+$')
    return bool(ip_pattern.match(hostname))

def prompt_for_three_vars(existing_vars):
    """
    Prompt ONLY for NODE_PORT, NODE_TCP_PORT, ADVERTISE_IP.
    If user hits Enter, keep existing .env value or use defaults.
    """
    # 1) NODE_PORT
    default_node_port = existing_vars.get('NODE_PORT', '8000')
    while True:
        node_port = input(
            f"Enter NODE_PORT (press Enter for default {default_node_port}): "
        ).strip()
        if not node_port:
            node_port = default_node_port
        if validate_port(node_port):
            existing_vars["NODE_PORT"] = node_port
            break
        print("Invalid port! Must be between 1024 and 65535.")

    # 2) NODE_TCP_PORT
    default_tcp_port = existing_vars.get('NODE_TCP_PORT', '8500')
    while True:
        node_tcp_port = input(
            f"Enter NODE_TCP_PORT (press Enter for default {default_tcp_port}): "
        ).strip()
        if not node_tcp_port:
            node_tcp_port = default_tcp_port
        if validate_port(node_tcp_port):
            existing_vars["NODE_TCP_PORT"] = node_tcp_port
            break
        print("Invalid port! Must be between 1024 and 65535.")

    # 3) ADVERTISE_IP
    default_ip = existing_vars.get('ADVERTISE_IP', 'localhost')
    while True:
        advertise_ip = input(
            f"Enter ADVERTISE_IP (e.g., example.com) [default {default_ip}]: "
        ).strip()
        if not advertise_ip:
            advertise_ip = default_ip
        if validate_hostname(advertise_ip):
            existing_vars["ADVERTISE_IP"] = advertise_ip
            break
        print("Invalid hostname/IP! Please enter a valid hostname or IP address.")

def set_default_vars(existing_vars):
    """
    Force certain environment variables to have the same defaults
    as your docker-compose.yml. If the user hasn’t defined them,
    we hard-code them here.
    """
    hardcoded_defaults = {
        "SECRET_KEY": "root",
        "ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "ENCRYPTION_PASSWORD": "s3cr3t_p@ssw0rd",
        "MPESA_CONSUMER_KEY": "qKWanfm4aw1FoduqOGGDBdv0f7UJf8Li",
        "MPESA_CONSUMER_SECRET": "07QvgShVQBVRF0eE",
        "BUSINESS_SHORT_CODE": "6290257",
        "PASSKEY": "390a62dc3a65c889ce9275360b7ee8c875e115c2bb0e3a312446f9a9740fb20d",
        "CALLBACK_URL": "https://example.com",
        "TESTING": "false",
        "POSTGRES_HOST": "postgres",
        "IS_VALIDATOR": "true",
    }
    for k, v in hardcoded_defaults.items():
        if k not in existing_vars or not existing_vars[k]:
            existing_vars[k] = v

def write_env(env_path, vars_dict):
    try:
        with open(env_path, 'w') as f:
            for k, v in vars_dict.items():
                f.write(f"{k}={v}\n")
    except Exception as e:
        print(f"Error writing .env: {e}")
        sys.exit(1)

def up(detached=False):
    """
    Bring up Docker containers using a persistent temp directory for docker-compose.yml.
    Store the temp directory path locally so we can reference it in 'down()'.
    """
    print("\nSetting up environment variables...")

    # 1) Create a persistent temp directory
    temp_dir_path = tempfile.mkdtemp()

    # 2) Copy Dockerfile + docker-compose.yml from inside the package
    docker_dir = resources.files("sokoweb.docker")
    shutil.copyfile(docker_dir / "Dockerfile", f"{temp_dir_path}/Dockerfile")
    shutil.copyfile(docker_dir / "docker-compose.yml", f"{temp_dir_path}/docker-compose.yml")

    # 3) Prepare .env in the temp directory
    env_path = Path(temp_dir_path) / ".env"
    user_env = Path.cwd() / ".env"
    if user_env.exists():
        shutil.copyfile(user_env, env_path)

    # 4) Load any existing vars, prompt for the 3 main ones, then set defaults
    existing_vars = read_existing_env(env_path)
    prompt_for_three_vars(existing_vars)
    set_default_vars(existing_vars)

    # If ADVERTISE_IP == "localhost", empty out bootstrap nodes
    if existing_vars["ADVERTISE_IP"] == "localhost":
        existing_vars["BOOTSTRAP_NODES"] = ""
    else:
        # If the user hasn't provided any value for BOOTSTRAP_NODES, set a default
        if "BOOTSTRAP_NODES" not in existing_vars or not existing_vars["BOOTSTRAP_NODES"]:
            # You can choose a default that suits you. Example below:
            existing_vars["BOOTSTRAP_NODES"] = "ec2-51-20-116-115.eu-north-1.compute.amazonaws.com:8000"

    # 5) Write .env variables back
    write_env(env_path, existing_vars)

    # 6) Save the temp directory path to a file in the current directory
    with open(SOKOWEB_TEMPFILE_NAME, "w") as f:
        f.write(temp_dir_path)

    # 7) Compose up with explicit project name
    print("\nStarting Docker containers...")
    compose_cmd = [
        "docker", "compose",
        "-f", "docker-compose.yml",
        "-p", "sokoweb",  # Add explicit project name
        "up", "--build"
    ]
    if detached:
        compose_cmd.append("-d")

    try:
        process = subprocess.run(
            compose_cmd,
            check=True,
            cwd=temp_dir_path
        )
        if process.returncode == 0:
            if detached:
                print("Successfully started Docker containers in detached mode.")
            else:
                print("Successfully started Docker containers.")
    except subprocess.CalledProcessError as e:
        print(f"Error starting Docker containers (exit code={e.returncode})")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)

def down():
    """
    Stop/remove containers (and volumes) by reading the temp_dir from .sokoweb_temp_dir.
    """
    print("Stopping Docker containers and removing volumes...")
    temp_file = Path.cwd() / SOKOWEB_TEMPFILE_NAME
    if not temp_file.exists():
        print(f"No {SOKOWEB_TEMPFILE_NAME} file found in the current directory.")
        print("Cannot determine where docker-compose.yml is located.")
        return

    with open(temp_file, "r") as f:
        temp_dir_path = f.read().strip()

    docker_compose_file = Path(temp_dir_path) / "docker-compose.yml"
    if not docker_compose_file.exists():
        print("No docker-compose.yml found in the stored temp directory path!")
        return

    try:
        subprocess.run(
            [
                "docker", "compose",
                "-f", str(docker_compose_file),
                "-p", "sokoweb",  # Add explicit project name
                "down", "-v"
            ],
            check=True,
            cwd=temp_dir_path
        )
        print("Successfully stopped and removed containers/volumes.")
    except subprocess.CalledProcessError as e:
        print(f"Error stopping Docker containers (exit code={e.returncode})")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)

    # (Optional) remove the temp directory and the .sokoweb_temp_dir file
    import shutil
    shutil.rmtree(temp_dir_path, ignore_errors=True)
    temp_file.unlink(missing_ok=True)