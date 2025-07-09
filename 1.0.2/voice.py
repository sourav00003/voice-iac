import speech_recognition as sr
import re
import subprocess
import boto3
import botocore


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

    tf_filled = tf_template.replace("__REGION__", region)\
                           .replace("__AMI__", ami)\
                           .replace("__INSTANCE_TYPE__", instance_type)\
                           .replace("__VOLUME_SIZE__", str(volume_size))

    print("Final main.tf content:\n", tf_filled)

    with open("main.tf", "w") as f:
        f.write(tf_filled)

    print("main.tf written successfully.")


# Terraform init and apply
def run_terraform():
    try:
        print("Running terraform init...")
        subprocess.run(["terraform", "init"], check=True)

        print("Running terraform apply (auto-approved)...")
        subprocess.run(["terraform", "apply", "-auto-approve"], check=True)

        print("Terraform apply completed.")

        print("📡 Fetching instance public IP...")
        output = subprocess.check_output(["terraform", "output", "instance_ip"], text=True)
        print(f"EC2 Public IP: {output.strip()}")

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
                line = line.split("#")[0].strip()  # Remove inline comments

            if line.startswith("bucket"):
                bucket = line.split("=")[1].strip().strip('"')
            elif line.startswith("key"):
                key = line.split("=")[1].strip().strip('"')

    return bucket, key


def delete_state_file(bucket_name, state_key="ec2/terraform.tfstate"):
    s3 = boto3.client("s3")
    try:
        s3.delete_object(Bucket=bucket_name, Key=state_key)
        print(f"State file '{state_key}' deleted from bucket '{bucket_name}'.")
    except Exception as e:
        print(f"Failed to delete state file: {e}")


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
                else:
                    print("Could not find backend config in main.tf.backup.")
            else:
                print("Keeping state file in S3.")

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



