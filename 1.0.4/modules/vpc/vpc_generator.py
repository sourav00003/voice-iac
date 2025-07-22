import os
from jinja2 import Environment, FileSystemLoader
from modules.mode_1.custom.vpc_template_parser import parse_vpc_custom_template

def generate_vpc_tf_from_yaml():
    # Parse only vpc_custom.yaml
    vpc_config = parse_vpc_custom_template()

    context = {
        "vpc_name": vpc_config.get("vpc_name", "default-like-vpc"),
        "region": vpc_config.get("region", "us-east-1"),  # Optional override
        "cidr_block": vpc_config["cidr_block"],
        "enable_dns_support": vpc_config.get("enable_dns_support", True),
        "enable_dns_hostnames": vpc_config.get("enable_dns_hostnames", True),
        "subnets": vpc_config["subnets"]
    }

    # Render the template
    template_dir = os.path.join("modules", "vpc")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("vpc_template.tf.j2")
    rendered = template.render(context)

    # Write output to terraform/vpc.tf
    os.makedirs("terraform", exist_ok=True)
    output_path = os.path.join("terraform", "vpc.tf")
    with open(output_path, "w") as f:
        f.write(rendered)

    print(f" VPC Terraform config generated at: {output_path}")




