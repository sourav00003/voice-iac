import os
import subprocess
import sys
from ansible.modules.ansible_parser import generate_ansible_playbook_from_yaml
from ansible.modules.inventory_generator import generate_inventory

# Constants
STATEFILE_NAME = "temp_terraform.tfstate"
INVENTORY_PATH = "ansible/playbook/inventory.yaml"
PLAYBOOK_PATH = "ansible/playbook/site.yaml"

def run_ansible(dry_run=False):
    print("\n[STEP 1] Downloading Terraform state from S3...")
    generate_inventory()

    print("\n[STEP 2] Generating site.yaml from custom_ansible.yaml...")
    generate_ansible_playbook_from_yaml(output_path=PLAYBOOK_PATH)

    print("\n[STEP 3] Preparing Ansible Playbook Execution...")
    ansible_cmd = [
        "ansible-playbook",
        "-i", INVENTORY_PATH,
        PLAYBOOK_PATH
    ]

    if dry_run:
        ansible_cmd.append("--check")
        print("[INFO] Executing Ansible in dry-run mode (--check)...")

    try:
        subprocess.run(ansible_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Ansible playbook failed: {e}")

    print("\n All steps completed.")

if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    run_ansible(dry_run=dry)
