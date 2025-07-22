### NEW
import os
import yaml
from modules.mode_1.custom.sg_generator import parse_custom_sg_rules
from modules.mode_1.custom.aws_utils import (
    get_default_vpc_and_subnet,
    get_subnet_for_existing_vpc
)
from modules.mode_1.fetchami import get_latest_amazon_linux_ami

def load_yaml_file(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"YAML file not found: {path}")
    with open(path, 'r') as file:
        return yaml.safe_load(file)

def expand_instances(instances_raw, region):
    latest_ami = get_latest_amazon_linux_ami(region)
    return [
        {
            "name": inst.get("name"),
            "instance_type": inst.get("instance_type"),
            "ami": latest_ami if inst.get("ami") == "auto" else inst.get("ami"),
            "volume_size": inst.get("volume_size"),
            "volume_type": inst.get("volume_type"),
            "number": inst.get("number", 1)
        }
        for inst in instances_raw
    ]

def generate_option1_context(custom, backend, sg_rules):
    vpc_info = get_default_vpc_and_subnet()
    return {
        "context_type": "option1",
        "action": custom.get("action", "create").lower(),
        "region": custom["region"],
        "key_name": custom["key_name"],
        "vpc_id": vpc_info["vpc_id"],
        "subnet_id": vpc_info["subnet_id"],
        "instances": expand_instances(custom["instances"], custom["region"]),
        "security_group": sg_rules[0] if sg_rules else {},
        "backend": backend
    }


def generate_option2_context(custom, backend, sg_rules):
    vpc_id = custom["vpc_id"]
    subnet_id = get_subnet_for_existing_vpc(vpc_id)
    return {
        "context_type": "option2",
        "action": custom.get("action", "create").lower(),
        "region": custom["region"],
        "key_name": custom["key_name"],
        "vpc_id": vpc_id,
        "subnet_id": subnet_id,
        "instances": expand_instances(custom["instances"], custom["region"]),
        "security_group": sg_rules[0] if sg_rules else {},
        "backend": backend
    }


def generate_option3_context(custom, backend, sg_rules):
    base_path = os.path.dirname(os.path.abspath(__file__))
    vpc_custom_path = os.path.join(base_path, "../../../yaml/vpc_custom.yaml")

    if not os.path.exists(vpc_custom_path):
        raise FileNotFoundError(f"Custom VPC YAML file not found at: {vpc_custom_path}")

    vpc_custom = load_yaml_file(vpc_custom_path)

    return {
        "context_type": "option3",
        "action": custom.get("action", "create").lower(),
        "region": custom["region"],
        "key_name": custom["key_name"],
        "vpc_custom": vpc_custom,
        "instances": expand_instances(custom["instances"], custom["region"]),
        "security_group": sg_rules[0] if sg_rules else {},
        "backend": backend
    }


def generate_template_context():
    base_path = os.path.dirname(os.path.abspath(__file__))

    custom_path = os.path.join(base_path, "../../../yaml/custom.yaml")
    backend_path = os.path.join(base_path, "../../../backend/custom_backend/custom_backend.yaml")
    sg_rules_path = os.path.join(base_path, "../../../custom_sg_rules.txt")

    custom = load_yaml_file(custom_path)
    backend = load_yaml_file(backend_path)
    sg_rules = parse_custom_sg_rules(file_path=sg_rules_path)

    vpc_id = custom.get("vpc_id", "").strip()
    vpc_custom_file = custom.get("vpc_custom_file", "").strip()

    if not vpc_id and not vpc_custom_file:
        return generate_option1_context(custom, backend, sg_rules)
    elif vpc_id:
        return generate_option2_context(custom, backend, sg_rules)
    elif vpc_custom_file:
        return generate_option3_context(custom, backend, sg_rules)
    else:
        raise ValueError("Invalid VPC configuration in custom.yaml")
