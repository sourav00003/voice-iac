import boto3
import os
import stat
import time


# Generate Key Pair
def create_key_pair(key_name="voiceiac-key"):
    ec2 = boto3.client("ec2")
    pem_path = os.path.join(os.getcwd(), f"{key_name}.pem")

    try:
        # Check if key already exists to avoid duplicate
        existing = ec2.describe_key_pairs(KeyNames=[key_name])
        print(f"Key pair '{key_name}' already exists.")
    except ec2.exceptions.ClientError as e:
        if "InvalidKeyPair.NotFound" in str(e):
            # Create new key pair
            print(f"Creating new key pair '{key_name}'...")
            response = ec2.create_key_pair(KeyName=key_name)
            private_key = response["KeyMaterial"]

            with open(pem_path, "w") as f:
                f.write(private_key)

            os.chmod(pem_path, stat.S_IRUSR)  # chmod 400 equivalent
            print(f"Key saved to {pem_path} with read-only permissions.")
        else:
            print(f"Error checking key pair: {e}")
            return None

    return key_name  # Return for Terraform attachment


# Delete the key pair after destroy
def delete_key_pair(key_name="voiceiac-key"):
    ec2 = boto3.client("ec2")
    try:
        ec2.delete_key_pair(KeyName=key_name)
        print(f"AWS Key pair '{key_name}' deleted successfully.")
    except Exception as e:
        print(f"Failed to delete key pair '{key_name}': {e}")

# Cleanup of the .pem file locally
def cleanup_pem_file(key_name="voiceiac-key"):
    pem_path = os.path.join(os.getcwd(), f"{key_name}.pem")
    if os.path.exists(pem_path):
        try:
            os.chmod(pem_path, stat.S_IWRITE)  # ensure write permission
            os.remove(pem_path)
            print(f"Deleted local private key: {pem_path}")
        except PermissionError:
            print(f"[Permission Error] Couldn't delete PEM file. Retrying...")
            time.sleep(1)
            try:
                os.remove(pem_path)
                print(f"Deleted after retry: {pem_path}")
            except Exception as e:
                print(f"[ERROR] Still failed: {e}")