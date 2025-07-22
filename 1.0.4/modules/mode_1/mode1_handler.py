# modules/mode_1/mode1_handler.py

import sys
import os
import yaml
from modules.mode_1.voice_handler import voice_to_text
from modules.mode_1.keyword_parser import extract_keywords
from modules.mode_1.ec2_generator import generate_main_tf_with_jinja
from modules.mode_1.terraform_runner import run_terraform, run_terraform_destroy

# =================  =====================

from modules.mode_1.custom.aws_utils import create_key_pair_if_needed
from modules.mode_1.custom.complete_parser import generate_template_context
from modules.mode_1.custom.ec2_only_generator import (
    generate_ec2_only_option1_tf,
    generate_ec2_only_option2_tf
)
from modules.mode_1.custom.vpc_ec2_generator import generate_vpc_ec2_option3_tf
from modules.mode_1.custom.terraform_runner2 import run_terraform

# ================= Voice Flow =====================



sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def handle_voice_command():
    """Handles EC2 provisioning through voice commands"""
    max_retries = 3
    attempt = 0
    parsed = None

    while attempt < max_retries:
        print(f"\n[Attempt {attempt + 1}/{max_retries}] Speak your command...")
        text = voice_to_text()

        if not text:
            print("No input detected. Please try again.")
            attempt += 1
            continue

        parsed = extract_keywords(text)
        print("Parsed Parameters:", parsed)

        if parsed.get("action") in ["create", "destroy"]:
            break
        else:
            print("Could not determine action. Please say 'create' or 'destroy' clearly.")
            attempt += 1

    if not parsed or parsed.get("action") not in ["create", "destroy"]:
        print("Max retries reached. Exiting.")
        return

    action = parsed.get("action")

    if action == "create":
        if parsed["region"] and parsed["instance_type"] and parsed["volume_size"]:
            print("[INFO] Generating Terraform configuration using Jinja2...")
            generate_main_tf_with_jinja(parsed)
            run_terraform()
        else:
            print("[ERROR] Missing required values like region, instance type, or volume size.")
    elif action == "destroy":
        print("[INFO] Destroying resources using Terraform...")
        run_terraform_destroy()


# ============== YAML-based Flow ===================

def handle_custom_yaml():
    """Handles EC2 provisioning or destruction using predefined custom.yaml (Options 1, 2, or 3)"""
    print("Parsing custom.yaml and preparing infrastructure...")

    try:
        context = generate_template_context()
        if not context:
            print("[ERROR] Failed to parse context.")
            return

        action = context.get("action", "").lower()
        context_type = context.get("context_type", "").lower()

        if action == "create":
            create_key_pair_if_needed()

            generator_map = {
                "option1": generate_ec2_only_option1_tf,
                "option2": generate_ec2_only_option2_tf,
                "option3": generate_vpc_ec2_option3_tf
            }

            generator_fn = generator_map.get(context_type)

            if generator_fn:
                print(f"[INFO] Executing Terraform generation for {context_type.upper()}...")
                generator_fn(context)
                run_terraform()
            else:
                print(f"[ERROR] Unknown context_type: {context_type}")

        elif action == "destroy":
            print("[INFO] Destroying infrastructure via Terraform...")
            from modules.mode_1.custom.terraform_runner2 import run_terraform_destroy
            run_terraform_destroy()

        else:
            print("[ERROR] 'action' must be either 'create' or 'destroy'.")

    except Exception as e:
        print(f"[ERROR] Failed during provisioning/destroy: {e}")


# ============== Dispatcher ===================
        

def run_mode1_flow():
    """Main dispatcher: asks whether to use custom.yaml or voice"""
    print("Mode 1: Voice-Based or YAML-Based IaC (choose below)\n")
    choice = input("Do you want to use custom.yaml for provisioning? (Y/N): ").strip().lower()

    if choice == 'y':
        handle_custom_yaml()
    else:
        handle_voice_command()


