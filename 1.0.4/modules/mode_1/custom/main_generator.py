import os
from modules.mode_1.custom.complete_parser import generate_template_context
from modules.mode_1.custom.ec2_only_generator import (
    generate_ec2_only_option1_tf,
    generate_ec2_only_option2_tf
)
from modules.mode_1.custom.vpc_ec2_generator import generate_vpc_ec2_option3_tf

def main():
    print("Parsing custom.yaml and other configurations...")
    context = generate_template_context()

    if not context:
        print("Failed to generate context.")
        return

    context_type = context.get("context_type")
    
    if context_type == "option1":
        print("[INFO] Detected Option 1: Using Default VPC.")
        generate_ec2_only_option1_tf(context)

    elif context_type == "option2":
        print("[INFO] Detected Option 2: Using Existing VPC ID.")
        generate_ec2_only_option2_tf(context)

    elif context_type == "option3":
        print("[INFO] Detected Option 3: Using Custom VPC YAML.")
        generate_vpc_ec2_option3_tf(context)

    else:
        print("Unknown context type. Please check your custom.yaml configuration.")

if __name__ == "__main__":
    main()
