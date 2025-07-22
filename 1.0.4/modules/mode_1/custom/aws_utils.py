import boto3
import os
import botocore.exceptions

# Constants
REGION = "us-east-1"
KEY_NAME = "custom-key"
PEM_PATH = os.path.join(os.getcwd(), f"{KEY_NAME}.pem")


def get_key_name_from_yaml():
    # For now, hardcoded. You can extend to read from custom.yaml.
    return KEY_NAME


def key_pair_exists(key_name=KEY_NAME, region=REGION):
    ec2 = boto3.client("ec2", region_name=region)
    try:
        ec2.describe_key_pairs(KeyNames=[key_name])
        return True
    except botocore.exceptions.ClientError as e:
        if "InvalidKeyPair.NotFound" in str(e):
            return False
        raise e


def create_key_pair_if_needed(key_name=KEY_NAME, region=REGION):
    pem_exists = os.path.exists(PEM_PATH)
    aws_key_exists = key_pair_exists(key_name, region)

    if pem_exists and aws_key_exists:
        print(f"[INFO] PEM file '{PEM_PATH}' already exists and key pair exists in AWS. Skipping key creation.")
        return

    print(f"[INFO] Creating key pair '{key_name}' in AWS and saving PEM to '{PEM_PATH}'...")
    ec2 = boto3.client("ec2", region_name=region)

    # Delete local PEM if stale
    if pem_exists:
        os.remove(PEM_PATH)

    key_pair = ec2.create_key_pair(KeyName=key_name)
    with open(PEM_PATH, "w") as pem_file:
        pem_file.write(key_pair["KeyMaterial"])
    os.chmod(PEM_PATH, 0o400)
    print(f"[SUCCESS] Key pair '{key_name}' created and saved locally.")


def delete_key_pair(key_name=KEY_NAME, region=REGION):
    ec2 = boto3.client("ec2", region_name=region)
    try:
        ec2.delete_key_pair(KeyName=key_name)
        print(f"[INFO] Key pair '{key_name}' deleted from AWS.")
    except botocore.exceptions.ClientError as e:
        if "InvalidKeyPair.NotFound" in str(e):
            print(f"[WARN] Key pair '{key_name}' already deleted or not found in AWS.")
        else:
            raise e


def cleanup_pem_file():
    if os.path.exists(PEM_PATH):
        os.remove(PEM_PATH)
        print(f"[INFO] Local PEM file '{PEM_PATH}' deleted.")
    else:
        print(f"[INFO] PEM file '{PEM_PATH}' not found locally.")


# Returns Default vpc and subnet
def get_default_vpc_and_subnet(region="us-east-1"):
    ec2 = boto3.client("ec2", region_name=region)

    # Get default VPC
    vpcs = ec2.describe_vpcs(Filters=[{"Name": "isDefault", "Values": ["true"]}])
    if not vpcs["Vpcs"]:
        raise Exception("No default VPC found.")
    vpc_id = vpcs["Vpcs"][0]["VpcId"]

    # Get one available subnet from default VPC
    subnets = ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])
    if not subnets["Subnets"]:
        raise Exception("No subnets found in default VPC.")
    subnet_id = subnets["Subnets"][0]["SubnetId"]

    return {"vpc_id": vpc_id, "subnet_id": subnet_id}

# Returns the subnet of existing vpc
def get_subnet_for_existing_vpc(vpc_id, region="us-east-1"):
    ec2 = boto3.client("ec2", region_name=region)

    # Verify the VPC exists
    vpcs = ec2.describe_vpcs(VpcIds=[vpc_id])
    if not vpcs["Vpcs"]:
        raise Exception(f"Provided VPC ID {vpc_id} does not exist.")

    # Get subnet from this VPC
    subnets = ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])
    if not subnets["Subnets"]:
        raise Exception(f"No subnets found in VPC {vpc_id}.")
    subnet_id = subnets["Subnets"][0]["SubnetId"]

    return {"vpc_id": vpc_id, "subnet_id": subnet_id}





