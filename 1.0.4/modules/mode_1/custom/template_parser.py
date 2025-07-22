import yaml
import os

def parse_custom_template(file_path="yaml/custom.yaml"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"[ERROR] custom.yaml not found at: {file_path}")

    with open(file_path, "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            raise ValueError(f"[ERROR] YAML parsing failed: {e}")

    # Required keys
    required_keys = ["region", "key_name", "instances"]
    for key in required_keys:
        if key not in config or not config[key]:
            raise ValueError(f"[ERROR] Missing required key: {key} in custom.yaml")

    # Normalize VPC keys
    config["vpc_id"] = config.get("vpc_id", "").strip()
    config["vpc_custom_file"] = config.get("vpc_custom_file", "").strip()

    # Validate instances
    for idx, instance in enumerate(config["instances"]):
        for field in ["name", "instance_type", "ami", "volume_size", "volume_type", "security_group", "number"]:
            if field not in instance:
                raise ValueError(f"[ERROR] Instance #{idx + 1} missing required field: {field}")

    return config


# Used to parse custom.yaml in main_generator.py
def extract_objective_from_yaml(file_path="yaml/custom.yaml"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"[ERROR] custom.yaml not found at: {file_path}")

    with open(file_path, "r") as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"[ERROR] YAML parsing failed: {e}")

    return config.get("objective", "create").strip().lower()




