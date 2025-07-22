import boto3

def get_latest_amazon_linux_ami(region):
    """
    Fetches the latest Amazon Linux 2 AMI ID for the given region.
    """
    try:
        ec2 = boto3.client('ec2', region_name=region)
        response = ec2.describe_images(
            Owners=['amazon'],
            Filters=[
                {'Name': 'name', 'Values': ['amzn2-ami-hvm-*-x86_64-gp2']},
                {'Name': 'state', 'Values': ['available']}
            ]
        )

        # Sort images by CreationDate (latest first)
        images = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)

        if images:
            latest_ami = images[0]['ImageId']
            print(f"[INFO] Latest Amazon Linux 2 AMI in {region}: {latest_ami}")
            return latest_ami
        else:
            print("[ERROR] No Amazon Linux 2 AMI found.")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to fetch AMI: {e}")
        return None
