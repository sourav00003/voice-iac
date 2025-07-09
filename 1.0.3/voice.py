import speech_recognition as sr
import re
import subprocess
import boto3
import botocore
import os
import time
import stat


def voice_to_text():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print(" Speak now... (Listening)")
        #audio = recognizer.listen(source)
        audio = recognizer.record(source, duration=6)

        try:
            print("Converting speech to text...")
            text = recognizer.recognize_google(audio)
            print(f" You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I could not understand your voice.")
        except sr.RequestError as e:
            print(f"Could not request results from Google API; {e}")


# List of common EC2 instance types (expand this as needed)
VALID_INSTANCE_TYPES = [
    "t2.nano", "t2.micro", "t2.small", "t2.medium", "t2.large",
    "t3.nano", "t3.micro", "t3.small", "t3.medium", "t3.large",
    "t3a.micro", "t3a.small", "t3a.medium"
]

# Fuzzy alias mapping for common voice recognition errors
FUZZY_INSTANCE_ALIASES = {
    "t2micro": "t2.micro",
    "t2microinstance": "t2.micro",
    "t2mic": "t2.micro",
    "t3micro": "t3.micro",
    "t3mic": "t3.micro",
    "t2small": "t2.small",
    "t2medium": "t2.medium",
    "82micro": "t2.micro",         
    "80tomicro": "t2.micro",       
    "a2micro": "t2.micro",
    "eightytwomicro": "t2.micro",  
}

# Fuzzy alias mapping for common voice recognition errors
FUZZY_REGION_ALIASES = {
    "useast1": "us-east-1",
    "us-eastone": "us-east-1",
    "useastone": "us-east-1",
    "u s east one": "us-east-1",
    "u.s.east.1": "us-east-1",
    "us east": "us-east-1",
    "east us": "us-east-1",
    "apsouth1": "ap-south-1",
    "apsouth": "ap-south-1",
    "south asia": "ap-south-1",
    "mumbai": "ap-south-1"
    # Add more fuzzy mappings as needed
}

VALID_REGIONS = [
    "us-east-1", "us-east-2", "us-west-1", "us-west-2",
    "ap-south-1", "ap-northeast-1", "ap-northeast-2", "ap-southeast-1", "ap-southeast-2",
    "eu-central-1", "eu-west-1", "eu-west-2", "eu-north-1",
    "sa-east-1", "ca-central-1", "af-south-1", "me-south-1"
]
VALID_ACTIONS = [
    "create", "launch", "destroy", "terminate", "delete"
]

def normalize(text):
    return text.lower().replace(" ", "").replace(".", "").replace("-", "")

def extract_keywords(text):
    original_text = text
    normalized_text = normalize(text)

    action = None
    instance_type = None
    region = None
    volume_size = None


    # Match action
    for a in VALID_ACTIONS:
        if a in normalized_text:
            # Map synonyms like terminate/delete to "destroy"
            if a in ["destroy", "terminate", "delete"]:
                action = "destroy"
            else:
                action = "create"
            break

    # Match instance type
    for itype in VALID_INSTANCE_TYPES:
        if normalize(itype) in normalized_text:
            instance_type = itype
            break

    # Match region from VALID_REGIONS
    for region_option in VALID_REGIONS:
        if normalize(region_option) in normalized_text:
            region = region_option
            break
    
    # Fuzzy Instances
    if not instance_type:
        for fuzzy, real in FUZZY_INSTANCE_ALIASES.items():
            if fuzzy in normalized_text:
                instance_type = real
                print(f"[Fuzzy match] Interpreted instance type as: {real}")
                break

    if not region:
        for fuzzy, real in FUZZY_REGION_ALIASES.items():
            if fuzzy in normalized_text:
                region = real
                print(f"[Fuzzy match] Interpreted region as: {real}")
                break

    # Match volume size
    volume_match = re.search(r"(\d+)\s*gb", original_text.lower())
    if volume_match:
        volume_size = volume_match.group(1)

    return {
        "action": action,
        "instance_type": instance_type,
        "region": region,
        "volume_size": volume_size
    }


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

# Delete dynamodb lock
def cleanup_dynamodb_lock(state_key="ec2/terraform.tfstate", table_name="voiceiac-tf-locks"):
    dynamodb = boto3.client("dynamodb")
    lock_id = state_key.split("/")[-1]  # Extract 'terraform.tfstate'
    try:
        dynamodb.delete_item(
            TableName=table_name,
            Key={"LockID": {"S": lock_id}}
        )
        print(f"[DynamoDB] Lock for '{lock_id}' removed from '{table_name}'.")
    except Exception as e:
        print(f"Failed to delete DynamoDB lock: {e}")

# Generate the main.tf file
def generate_main_tf_from_backup(params):
    with open("main.tf.backup", "r") as f:
        tf_template = f.read()

    ami_map = {
        "ap-south-1": "ami-05ffe3c48a9991133",
        "us-east-1": "ami-05ffe3c48a9991133",
    }

    region = params.get("region")
    ami = ami_map.get(region, "ami-05ffe3c48a9991133")
    instance_type = params.get("instance_type")
    volume_size = params.get("volume_size")

    if not all([region, instance_type, volume_size]):
        print("Some values are missing — can't generate main.tf")
        return

    # Ask for SSH access
    print("Do you want SSH access to the instance? \n")
    ssh_answer = voice_to_text() or ""
    ssh_required = "yes" in ssh_answer.lower()

    if ssh_required:
        # Create key and get key name
        key_name = create_key_pair()
        sg_block = '''
resource "aws_security_group" "ssh_sg" {
  name        = "ssh_sg"
  description = "Allow SSH"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "ssh-sg"
  }
}
'''
        sg_attachment = 'vpc_security_group_ids = [aws_security_group.ssh_sg.id]'
    else:
        sg_block = ''
        sg_attachment = ''
        key_name = ""  # No SSH, no key

    # Replace placeholders in main.tf.backup
    tf_filled = tf_template.replace("__REGION__", region)\
                           .replace("__AMI__", ami)\
                           .replace("__INSTANCE_TYPE__", instance_type)\
                           .replace("__VOLUME_SIZE__", str(volume_size))\
                           .replace("<% sg_block %>", sg_block)\
                           .replace("<% vpc_sg_attachment %>", sg_attachment)\
                           .replace("__KEY_NAME__", key_name)

    with open("main.tf", "w") as f:
        f.write(tf_filled)

    print("main.tf written successfully.")
    if ssh_required:
        print("SSH Security Group and key added.")
    else:
        print("No SSH access requested.")


# Terraform init and apply
def run_terraform():
    try:
        print("Formatting main.tf...")
        subprocess.run(["terraform", "fmt"], check=True)

        print("Running terraform init...")
        subprocess.run(["terraform", "init"], check=True)

        print("Running terraform apply (auto-approved)...")
        subprocess.run(["terraform", "apply", "-auto-approve"], check=True)

        print("Terraform apply completed.")

        print("Fetching instance public IP...")
        output = subprocess.check_output(["terraform", "output", "instance_ip"], text=True)
        public_ip = output.strip()
        print(f"EC2 Public IP: {public_ip}")

        print("\n To login to the EC2 instance, use this command:")
        print(f"ssh -i voiceiac-key.pem ec2-user@{public_ip}")
        print("\n NOTE: If it's an Ubuntu AMI, use `ubuntu` instead of `ec2-user`.")

    except subprocess.CalledProcessError as err:
        print(f"Terraform failed: {err}")
    except FileNotFoundError:
        print("Terraform CLI not found. Please make sure it's installed and in PATH.")



# Voice Confirmation for Destroy
def get_voice_confirmation():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say 'yes' to confirm destroy, or 'no' to cancel:")
        audio = recognizer.listen(source, phrase_time_limit=4)

    try:
        response = recognizer.recognize_google(audio).lower()
        print(f"You said: {response}")
        return response
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return ""
    except sr.RequestError as e:
        print(f"Google API error: {e}")
        return ""

# Destruction Part

def parse_backend_config(file_path="main.tf.backup"):
    bucket = None
    key = None

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if "#" in line:
                line = line.split("#")[0].strip()

            if line.startswith("bucket"):
                bucket = line.split("=")[1].strip().strip('"')
            elif line.startswith("key"):
                value = line.split("=")[1].strip().strip('"')
                # Skip placeholder
                if "__KEY_NAME__" not in value:
                    key = value

    # Fallback default if placeholder still present
    if not key:
        key = "ec2/terraform.tfstate"

    return bucket, key


def delete_state_file(bucket_name, state_key="ec2/terraform.tfstate"):
    s3 = boto3.client("s3")
    dynamodb = boto3.client("dynamodb")

    try:
        # Delete from S3
        s3.delete_object(Bucket=bucket_name, Key=state_key)
        print(f"[S3] State file '{state_key}' deleted from bucket '{bucket_name}'.")

        # Delete lock from DynamoDB
        dynamodb.delete_item(
            TableName="voiceiac-tf-locks",
            Key={"LockID": {"S": state_key}}  # LockID is usually same as state_key
        )
        print(f"[DynamoDB] Lock for '{state_key}' deleted from 'voiceiac-tf-locks' table.")

    except Exception as e:
        print(f"Cleanup failed: {e}")


def run_terraform_destroy():
    try:
        response = get_voice_confirmation()
        if "yes" in response:
            print("Confirmed. Running terraform destroy (auto-approved)...")
            subprocess.run(["terraform", "destroy", "-auto-approve"], check=True)
            print("Terraform destroy completed.")

            print("Do you want to delete the Terraform state file from S3?")
            voice_confirm = get_voice_confirmation()
            if "yes" in voice_confirm:
                bucket, key = parse_backend_config()
                if bucket and key:
                    delete_state_file(bucket, key)
                    cleanup_dynamodb_lock(key)  # ✅ Clean DynamoDB lock here
                else:
                    print("Could not find backend config in main.tf.backup.")
                    cleanup_dynamodb_lock()  # fallback with default
            else:
                print("Keeping state file in S3.")

            # Clean up AWS key pair
            delete_key_pair("voiceiac-key")

            # Clean up local .pem file
            cleanup_pem_file("voiceiac-key")
        else:
            print("Destroy operation cancelled.")

    except subprocess.CalledProcessError as err:
        print(f"Terraform destroy failed: {err}")
    except FileNotFoundError:
        print("Terraform CLI not found. Please make sure it's installed and in PATH.")


if __name__ == "__main__":
    text = voice_to_text()
    if text:
        parsed = extract_keywords(text)
        print("Parsed Parameters:", parsed)

        action = parsed.get("action")

        if action == "create":
            if parsed["region"] and parsed["instance_type"] and parsed["volume_size"]:
                generate_main_tf_from_backup(parsed)
                run_terraform()
            else:
                print("Missing required values like region, instance type, or volume size.")

        elif action == "destroy":
            run_terraform_destroy()

        else:
            print("Could not determine action. Please say 'create' or 'destroy' clearly.")
