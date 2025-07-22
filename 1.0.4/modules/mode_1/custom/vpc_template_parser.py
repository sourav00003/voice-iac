import yaml
import os

def parse_vpc_custom_template(yaml_path="yaml/vpc_custom.yaml"):
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"YAML file not found at {yaml_path}")

    with open(yaml_path, "r") as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise Exception(f"Error parsing VPC YAML: {e}")

    required_keys = ["cidr_block", "subnets"]
    for key in required_keys:
        if key not in config:
            raise KeyError(f"Missing required VPC key: '{key}' in vpc_custom.yaml")

    # Optional: Validate subnets have required fields
    for subnet in config["subnets"]:
        if "name" not in subnet or "cidr_block" not in subnet or "az" not in subnet:
            raise KeyError("Each subnet must have 'name', 'cidr_block', and 'az' defined.")

    return config
