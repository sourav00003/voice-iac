import boto3
import json
import os
import yaml

# Constants
BUCKET_NAME = "customiac"
STATE_KEY = "custom/terraform.tfstate"
REGION = "us-east-1"
LOCAL_STATE_PATH = "temp_terraform.tfstate"
INVENTORY_OUTPUT = "ansible/playbook/inventory.yaml"

def download_state_file(bucket, key, region, local_path):
    s3 = boto3.client("s3", region_name=region)
    s3.download_file(bucket, key, local_path)
    print(f"[INFO] Downloaded state file to {local_path}")

def convert_to_wsl_path(win_path):
    """
    Converts Windows path (D:\path\to\file) to WSL path (/mnt/d/path/to/file)
    """
    drive, rest = os.path.splitdrive(win_path)
    drive_letter = drive.rstrip(":").lower()
    rest_path = rest.replace("\\", "/")
    return f"/mnt/{drive_letter}{rest_path}"

def parse_tfstate_for_inventory(state_path):
    if not os.path.exists(state_path):
        raise FileNotFoundError(f"[ERROR] State file not found: {state_path}")

    with open(state_path, 'r') as f:
        state = json.load(f)

    hosts = {}

    for res in state.get("resources", []):
        if res["type"] == "aws_instance":
            for inst in res.get("instances", []):
                attrs = inst.get("attributes", {})
                public_ip = attrs.get("public_ip")
                key_name = attrs.get("key_name")
                if public_ip and key_name:
                    abs_path = os.path.abspath(f"{key_name}.pem")

                    if not os.path.exists(abs_path):
                        print(f"[WARNING] PEM file not found: {abs_path}")

                    # Convert Windows-style path to WSL-compatible path if not on native Windows
                    pem_path = convert_to_wsl_path(abs_path)

                    hosts[public_ip] = {
                        "ansible_user": "ec2-user",
                        "ansible_ssh_private_key_file": pem_path
                    }

    return {"all": {"hosts": hosts}}

def write_inventory_yaml(inventory_data, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        yaml.dump(inventory_data, f, sort_keys=False)
    print(f"[SUCCESS] Inventory written to {output_path}")

def cleanup_temp_file(path):
    if os.path.exists(path):
        os.remove(path)
        print(f"[INFO] Deleted temporary file {path}")

def generate_inventory():
    print("\n[STEP 1] Downloading Terraform state file from S3...")
    download_state_file(BUCKET_NAME, STATE_KEY, REGION, LOCAL_STATE_PATH)

    print("[STEP 2] Parsing Terraform state file for EC2 instances...")
    inventory = parse_tfstate_for_inventory(LOCAL_STATE_PATH)

    print("[STEP 3] Writing inventory YAML...")
    write_inventory_yaml(inventory, INVENTORY_OUTPUT)

    print("[STEP 4] Cleaning up temporary state file...")
    cleanup_temp_file(LOCAL_STATE_PATH)  # Uncomment if desired

    print("Inventory generation complete.")
