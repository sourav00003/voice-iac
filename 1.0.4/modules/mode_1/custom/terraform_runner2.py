import subprocess
import os

from modules.mode_1.custom.aws_utils import (
    get_key_name_from_yaml,
    create_key_pair_if_needed,
    delete_key_pair,
    cleanup_pem_file
)

def run_terraform():
    tf_dir = os.path.join(os.getcwd(), "terraform")

    print("Checking/creating key pair before provisioning...")
    key_name = get_key_name_from_yaml()
    create_key_pair_if_needed()

    try:
        print("Formatting Terraform files...")
        subprocess.run(["terraform", "fmt"], check=True, cwd=tf_dir)

        # Step 1: Clean .terraform folder (optional but safe)
        terraform_dir = os.path.join(tf_dir, ".terraform")
        if os.path.exists(terraform_dir):
            import shutil
            shutil.rmtree(terraform_dir)
            print("Cleaned previous .terraform directory.")

        # Step 2: Re-initialize AFTER backend config is generated
        print("Reinitializing terraform with backend...")
        subprocess.run(["terraform", "init", "-reconfigure"], check=True, cwd=tf_dir)

        # Step 3: Apply
        print("Applying Terraform configuration (auto-approved)...")
        subprocess.run(["terraform", "apply", "-auto-approve", "-input=false"], check=True, cwd=tf_dir)

        print("Terraform apply completed.")

        try:
            output = subprocess.check_output(["terraform", "output", "instance_ip"], cwd=tf_dir, text=True)
            public_ip = output.strip()
            print(f"Instance IP: {public_ip}")
            print(f"SSH command: ssh -i {key_name}.pem ec2-user@{public_ip}")
        except subprocess.CalledProcessError:
            print("'instance_ip' output not defined or not retrievable.")

    except subprocess.CalledProcessError as err:
        print(f"Terraform error: {err}")
    except FileNotFoundError:
        print("Terraform CLI not found. Please install and ensure it's in PATH.")


def run_terraform_destroy():
    tf_dir = os.path.join(os.getcwd(), "terraform")
    #key_name = get_key_name_from_yaml()

    confirm = input("Are you sure you want to destroy the infrastructure? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Destroy cancelled by user.")
        return

    try:
        print("Running terraform init with reconfigure before destroy...")
        subprocess.run(["terraform", "init", "-reconfigure"], check=True, cwd=tf_dir)

        print("Running terraform destroy (auto-approved)...")
        subprocess.run(["terraform", "destroy", "-auto-approve"], check=True, cwd=tf_dir)
        print("Terraform destroy completed.")

        # Cleanup key pair and PEM
        print("Cleaning up key pair and PEM...")
        delete_key_pair()
        cleanup_pem_file()

    except subprocess.CalledProcessError as err:
        print(f"Terraform destroy failed: {err}")
    except FileNotFoundError:
        print("Terraform CLI not found. Please install and ensure it's in PATH.")
