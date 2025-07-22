import boto3

def validate_vpc_exists(vpc_id, region):
    """
    Checks if the provided VPC ID exists in the specified region.
    :param vpc_id: The VPC ID to validate (e.g., 'vpc-xxxxxxxx')
    :param region: AWS region (e.g., 'us-east-1')
    :return: True if VPC exists, False otherwise
    """
    try:
        ec2 = boto3.client('ec2', region_name=region)
        response = ec2.describe_vpcs(VpcIds=[vpc_id])
        return len(response['Vpcs']) > 0
    except ec2.exceptions.ClientError as e:
        if "InvalidVpcID.NotFound" in str(e):
            print(f"[ERROR] VPC ID {vpc_id} not found in region {region}.")
            return False
        else:
            print(f"[ERROR] Unexpected error while validating VPC: {e}")
            raise
