import subprocess
import os
import speech_recognition as sr
from modules.mode_1.state_manager import parse_backend_config, delete_state_file, cleanup_dynamodb_lock
from modules.mode_1.aws_utils import delete_key_pair, cleanup_pem_file
from modules.utils.retry_helper import get_confirmation_with_retry  # stays unchanged (shared utility)

# Terraform init and apply
def run_terraform():
    tf_dir = os.path.join(os.getcwd(), "state")  # Run terraform inside state/

    try:
        print("Formatting main.tf...")
        subprocess.run(["terraform", "fmt"], check=True, cwd=tf_dir)

        print("Running terraform init...")
        subprocess.run(["terraform", "init", "-reconfigure"], check=True, cwd=tf_dir)

        print("Running terraform apply (auto-approved)...")
        subprocess.run(["terraform", "apply", "-auto-approve", "-input=false"], check=True, cwd=tf_dir)

        print("Terraform apply completed.")

        print("📡 Fetching instance public IP...")
        output = subprocess.check_output(["terraform", "output", "instance_ip"], cwd=tf_dir, text=True)
        public_ip = output.strip()
        print(f"EC2 Public IP: {public_ip}")

        print("\n To login to the EC2 instance, use this command:")
        print(f"ssh -i voiceiac-key.pem ec2-user@{public_ip}")
        print("\n NOTE: If it's an Ubuntu AMI, use `ubuntu` instead of `ec2-user`.")

    except subprocess.CalledProcessError as err:
        print(f"Terraform failed: {err}")
    except FileNotFoundError:
        print("Terraform CLI not found. Please make sure it's installed and in PATH.")

# Destroy Infra
def run_terraform_destroy():
    tf_dir = os.path.join(os.getcwd(), "state")

    try:
        if not get_confirmation_with_retry("Confirm destroy"):
            print("Destroy operation cancelled.")
            return

        print("Confirmed. Running terraform destroy (auto-approved)...")
        subprocess.run(["terraform", "destroy", "-auto-approve"], check=True, cwd=tf_dir)
        print("Terraform destroy completed.")

        if get_confirmation_with_retry("Do you want to delete the Terraform state file from S3?"):
            backend_config = parse_backend_config()
            bucket = backend_config.get("bucket")
            key = backend_config.get("key")

            if bucket and key:
                delete_state_file(bucket, key)
                prefix = f"{bucket}/{key}"
                cleanup_dynamodb_lock(prefix)
            else:
                print("Could not find backend config in backend.yaml.")
        else:
            print("Keeping state file in S3.")

        # Cleanup AWS key pair and PEM file
        delete_key_pair("voiceiac-key")
        cleanup_pem_file("voiceiac-key")

    except subprocess.CalledProcessError as err:
        print(f"Terraform destroy failed: {err}")
    except FileNotFoundError:
        print("Terraform CLI not found. Please make sure it's installed and in PATH.")
