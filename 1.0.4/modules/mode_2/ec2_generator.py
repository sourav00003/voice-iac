import os
from jinja2 import Environment, FileSystemLoader
from modules.mode_2.aws_utils import create_key_pair
from modules.mode_2.fetchami import get_latest_amazon_linux_ami
from modules.mode_2.sg_generator import parse_sg_rules
from modules.utils.file_searcher import find_file_within_project  # stays the same (in shared utils)
 

def generate_main_tf_with_jinja(params):
    """
    Generates main.tf using Jinja2 template and dynamic AMI fetching.
    Includes Security Groups parsed from custom_sg_rules.txt.
    """

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # 🔍 Find the template path dynamically
    template_filename = "main_voice.tf.j2"
    template_path = find_file_within_project(template_filename, project_root)

    if not template_path:
        print(f"[ERROR] Template file '{template_filename}' not found in project.")
        return

    template_dir = os.path.dirname(template_path)
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

    rendered = template.render(
        region=region,
        ami=ami,
        instance_type=instance_type,
        volume_size=volume_size,
        key_name=key_name,
        security_groups=security_groups
    )

    os.makedirs('state', exist_ok=True)
    with open('state/main.tf', 'w') as f:
        f.write(rendered)

    print("[INFO] main.tf generated successfully using Jinja2 template.")
    if key_name:
        print(f"[INFO] SSH Key '{key_name}' added for EC2 login.")
    else:
        print("[INFO] No SSH key created.")
