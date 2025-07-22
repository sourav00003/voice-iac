import os
import yaml
from jinja2 import Environment, FileSystemLoader
from modules.mode_1.aws_utils import create_key_pair
from modules.mode_1.fetchami import get_latest_amazon_linux_ami
from modules.mode_1.sg_generator import parse_sg_rules
from modules.mode_1.state_manager import parse_backend_config  # Now returns a dict


# Generate main.tf file from voice commands
def generate_main_tf_with_jinja(params):
    """
    Generates main.tf using Jinja2 template and dynamic AMI fetching.
    Includes backend config and Security Groups parsed from custom_sg_rules.txt.
    """

    # Path to templates inside mode_1
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    template_filename = "main_voice.tf.j2"
    template_path = os.path.join(template_dir, template_filename)

    if not os.path.exists(template_path):
        print(f"[ERROR] Template file '{template_filename}' not found in {template_dir}")
        return

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_filename)

    region = params.get("region")
    instance_type = params.get("instance_type")
    volume_size = params.get("volume_size")

    if not all([region, instance_type, volume_size]):
        print("[ERROR] Missing values — cannot generate main.tf")
        return

    ami = get_latest_amazon_linux_ami(region)
    if not ami:
        print("[ERROR] Could not fetch AMI — exiting.")
        return

    key_name = None
    security_groups = []

    if os.path.exists("custom_sg_rules.txt"):
        security_groups = parse_sg_rules("custom_sg_rules.txt")
        ssh_rule_found = any(
            any(rule.get("port") == 22 for rule in sg.get("ingress", []))
            for sg in security_groups
        )
        if ssh_rule_found:
            key_name = create_key_pair("voiceiac-key")
            print("[INFO] SSH rule detected → Key pair created.")
        else:
            print("[INFO] No SSH rule found → Skipping key pair.")
    else:
        print("[INFO] No custom_sg_rules.txt → Skipping SG and key pair.")

    # Load backend config from YAML
    backend_config = parse_backend_config()
    bucket = backend_config.get("bucket")
    key = backend_config.get("key", "ec2/terraform.tfstate")
    backend_region = backend_config.get("region")
    dynamodb_table = backend_config.get("dynamodb_table")

    if not all([bucket, backend_region, dynamodb_table]):
        print("[ERROR] Missing backend values. Check backend.yaml.")
        return

    rendered = template.render(
        region=region,
        ami=ami,
        instance_type=instance_type,
        volume_size=volume_size,
        key_name=key_name,
        security_groups=security_groups,
        backend_bucket=bucket,
        backend_key=key,
        backend_region=backend_region,
        dynamodb_table=dynamodb_table
    )

    os.makedirs('state', exist_ok=True)
    with open('state/main.tf', 'w') as f:
        f.write(rendered)

    print("[INFO] main.tf generated successfully using Jinja2 template.")
    if key_name:
        print(f"[INFO] SSH Key '{key_name}' added for EC2 login.")
    else:
        print("[INFO] No SSH key created.")



############################################################################################################
    # Generate main.tf file from custom yaml file


def generate_main_tf_from_custom_yaml(yaml_path="custom.yaml"):
    if not os.path.exists(yaml_path):
        print(f"[ERROR] custom.yaml not found at {yaml_path}")
        return

    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)

    instances = config.get("instances", [])
    if not instances:
        print("[ERROR] No EC2 instances defined in custom.yaml.")
        return

    for instance in instances:
        if instance.get("ami", "auto") == "auto":
            instance["ami"] = get_latest_amazon_linux_ami(config.get("region", "us-east-1"))

    bucket, key, backend_region, dynamodb_table = parse_backend_config()

    template_data = {
        "region": config.get("region", "us-east-1"),
        "instances": instances,
        "key_name": config.get("key_name", "custom-key"),
        "bucket": bucket,
        "key": key,
        "backend_region": backend_region,
        "dynamodb_table": dynamodb_table
    }

    # Jinja2 setup for the new template
    template_dir = os.path.join(os.path.dirname(__file__), "../../templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("main_custom.tf.j2")

    output = template.render(template_data)

    with open("main.tf", "w") as f:
        f.write(output)

    print("[INFO] main.tf generated from custom.yaml using Jinja2.")