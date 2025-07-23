# Voice-IaC – Voice Controlled Infrastructure as Code

Voice-IaC is an Infrastructure-as-Code (IaC) system built with Python and Terraform that allows you to create or destroy AWS EC2 infrastructure using either voice commands or simple declarative YAML configuration. It also supports automated post-provisioning with Ansible for seamless end-to-end cloud setup.

<p align="center">
  <img src="https://drive.google.com/uc?export=view&id=1Ws4I8rvVwtZ3xqRXT57_bXG11gne66aJ" width="250" alt="Angry Coder"/>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://drive.google.com/uc?export=view&id=1OmGYeYoZd5j4brLn2J4r7blsBQAuS8Tt" width="250" alt="Happy Coder"/>
</p>

<p align="center"><strong>From this... ➡️ to this</strong></p>
<p align="center">💥 This tool takes you from <em>rage-quitting DevOps</em> → to <strong>happy automation wizard ✨</strong></p>



## Features
- 🎙️ Voice-to-Text provisioning using Google Speech Recognition
- 📄 YAML-based infrastructure support via custom.yaml and vpc_custom.yaml
- 🧠 Extracts key parameters: instance_type, region, volume_size, objective, and vpc mode
- ⚙️ Dynamically generates main.tf using Jinja2 templates
- 🗺️ Supports three VPC modes:
        Use default VPC
        Use existing VPC ID
        Create custom VPC from YAML
- 🔐 Adds optional SSH access via secure key pair and security group logic
- 📦 Supports inline or file-based security group rule definitions
- 🚀 Runs terraform init, apply, and destroy programmatically with rollback handling
- 📚 Maintains backend state in S3 and uses DynamoDB for state locking
- 🧹 On destroy: removes EC2s, deletes key pairs, SGs, S3 state, and DynamoDB lock
- 🛠️ Automated post-provisioning with Ansible — dynamically generates inventory from Terraform state and applies custom configuration via templated playbooks for seamless remote instance setup

## Project Structure
project_structure_detailed = """
```bash
1.0.4/
├── ansible/
│   ├── modules/
│   │   ├── allowed_packages.py         # Defines allowed packages for Ansible
│   │   ├── ansible_parser.py           # Parses custom_ansible.yaml
│   │   ├── ansible_runner.py           # Executes Ansible playbooks
│   │   ├── inventory_generator.py      # Generates inventory.yaml from TF state
│   └── playbook/
│       ├── inventory.yaml              # Generated from TF state
│       └── site.yaml                   # Rendered Ansible playbook
├── backend/
│   └── backend.yaml                    # S3 + DynamoDB backend config
├── modules/
│   ├── utils/
│   │   └── file_finder.py              # Utility to locate files dynamically
│   ├── mode_1/
│   │   ├── fetchami.py                 # AMI fetch utility (latest Amazon Linux 2)
│   │   ├── aws_utils.py                # Handles key pair creation, subnet lookup
│   │   ├── ec2_generator.py            # Voice-based EC2 TF generator (default VPC)
│   │   ├── keyword_parser.py           # Extracts keywords from voice input
│   │   ├── mode1_handler.py            # Master controller for Mode 1 (voice + YAML)
│   │   ├── sg_generator.py             # Parses inline SG rules for Mode 1
│   │   ├── state_manager.py            # Handles DynamoDB lock cleanup
│   │   ├── terraform_runner.py         # Applies/destroys TF in Mode 1
│   │   ├── voice_handler.py            # Handles microphone input + STT
│   │   └── custom/
│   │       ├── aws_utils.py              # Handles key pair and VPC/subnet resolution
│   │       ├── complete_parser.py        # Parses all YAMLs, backend, SG rules
│   │       ├── ec2_only_generator.py     # Generates TF for default/existing VPC
│   │       ├── vpc_ec2_generator.py      # Generates TF for custom VPC + EC2
│   │       ├── sg_generator.py           # Parses SG rule text file
│   │       ├── vpc_checker.py            # Verifies if given VPC ID exists
│   │       └── main_generator.py         # Main orchestrator for YAML flow
├── templates/
│   ├── main.tf.j2                     # Template for EC2-only infra
│   ├── vpc_ec2.tf.j2                  # Template for VPC + EC2 infra
│   └── playbook.j2                    # Template to render Ansible playbook
├── yaml/
│   ├── custom.yaml                    # User-defined EC2, VPC, SG config
│   ├── vpc_custom.yaml                # Defines custom VPC and subnet structure
│   └── custom_ansible.yaml            # Specifies post-provisioning Ansible tasks
├── main.py                            # Entry point to start Mode 1 or Mode 2
├── mode1_handler.py                   # Handles Mode 1 (voice/YAML-based provisioning)
├── mode2_handler.py                   # Legacy handler for Mode 2 (deprecated)
├── terraform_runner2.py               # Terraform wrapper used for YAML flow
├── custom_sg_rules.txt                # Optional security group rules file
├── test.py                            # SG parser test script

```
## How It Works (v1.0.4)
1. Start provisioning using either method:

    -🎙️ Voice Command
        Example:
        - "Create a t2.micro instance in us-east-1 with 8GB volume"
        - "Destroy the infrastructure"

    📄 YAML Configuration
        - Define infrastructure via:
        - custom.yaml: EC2 config, SG, VPC mode
        - vpc_custom.yaml: (optional) for defining custom VPC + subnets
        - custom_ansible.yaml: (optional) for post-setup Ansible tasks


2. Input Extraction & Validation:
    - Extracted fields include:
        - Action: create / destroy
        - Instance Type: t2.micro, t3a.small, etc.
        - Region: us-east-1, ap-south-1, etc. (fuzzy matched)
        - Volume Size: 8, 10, etc.
    - VPC Handling:
        - Use default VPC
        - Use an existing VPC ID
        - Provision a custom VPC via vpc_custom.yaml
    - Security Group Logic:
        - Use existing SG by name
        - Or define custom SG rules via custom_sg_rules.txt

3. Terraform Configuration Generation:
    - YAML is parsed and merged with backend, SG, and AMI resolution
    - Infrastructure templates (main.tf.j2, vpc_ec2.tf.j2) are rendered via Jinja2
    - Injects key pair block and SG rules dynamically
    - Generates a complete main.tf in the terraform/ directory

4. Terraform Execution:
    - terraform init to initialize the backend
    - terraform apply to provision resources
    - terraform destroy (after confirmation or via YAML) to teardown

5. Post-Provision Configuration with Ansible:
    - Downloads and parses Terraform state from S3
    - Dynamically generates an Ansible inventory
    - Renders site.yaml playbook using playbook.j2
    - Executes remote configuration over SSH

6.  Cleanup Logic on Destroy:
    - Terminates EC2 instances
    - Deletes custom or attached security groups
    - Removes AWS key pair and local .pem file
    - Deletes Terraform state from S3
    - Removes state lock from DynamoDB

## Tech Stack

| Layer           | Tools / Services                                                    |
|------------------|---------------------------------------------------------------------|
| Voice Input       | Python (`SpeechRecognition`, `PyAudio`)                            |
| Text Processing   | Regex, Fuzzy Matching, Keyword Extraction                          |
| YAML Parsing      | PyYAML, Structured parsing for `custom.yaml`, `vpc_custom.yaml`    |
| Template Engine   | Jinja2 (for Terraform and Ansible file generation)                 |
| IaC Engine        | Terraform (AWS Provider, S3 Backend, DynamoDB Locking)             |
| Config Management | Ansible (Dynamic Inventory, Playbook via `playbook.j2`)            |
| Cloud Infra       | AWS (EC2, EBS, Key Pair, Security Groups, VPC/Subnets)             |
| Automation Logic  | Python subprocess, `boto3` for AWS API interactions                |
| Backend State     | S3 (Terraform state) + DynamoDB (state locking)                    |

## Getting Started
## Prerequisites
   - Python 3.8+ installed
   - Terraform CLI installed and added to your system’s PATH
   - AWS CLI installed and configured with valid credentials
     ```bash
      aws configure
     ```
   - Microphone enabled and working (for voice-driven)
   -  IAM Permissions on your AWS account to:
       - Launch and terminate EC2 instances
       - Create/delete security groups and key pairs
       - Create/manage S3 buckets (for storing Terraform state)
       - Create/manage DynamoDB tables (for Terraform locking)
   - (Optional but Recommended) Ansible installed  
      ```bash
     pip install ansible
      ```
   - (For YAML provisioning) Required YAML files:
      - yaml/custom.yaml
      - (Optional) yaml/vpc_custom.yaml
      - (Optional) yaml/custom_ansible.yaml

## Python Dependencies

```bash
    pip install SpeechRecognition
    pip install pyaudio
    pip install boto3
    pip install PyYAML
    pip install jinja2
    pip install ansible
```

## Example Voice Commands
## Create Commands
   - "Create a t2.micro instance in ap-south-1 with 8GB volume"
   - "Launch a t3.small instance in us-west-2 with 10GB storage"
   - "Provision a t2.medium server in Mumbai" (fuzzy match → ap-south-1)
   - "Create two t3.micro instances in us-east-1 with 20GB disk"
## Destroy Commands
   - "Destroy the infrastructure"
   - "Terminate the EC2 instance in us-east-1"
   - "Delete all"
   - "Tear down everything" (fuzzy match supported)

## Example YAML Commands
Create Configs
```bash
# Minimal EC2 in default VPC
action: destroy
region: us-east-1
key_name: custom-key
vpc_id: ""  
vpc_custom_file: ""
instances:
  - name: dev-ec2
    instance_type: t2.micro
    ami: auto
    volume_size: 8
    ssh: true
    security_groups:
      - default
```
---
# Destroy Command via YAML
```bash
objective: destroy
```
## Notes
   
   - Only predefined EC2 instance types and AWS regions are supported (extensible via config)
   - Voice-based destroy functionality is supported from v1.0.1+
   - Backend state management via S3 + DynamoDB introduced in v1.0.2
   - Fuzzy matching allows for forgiving input like:
      - "t2mic" → t2.micro
      - "Mumbai" → ap-south-1
   - Ensure your microphone is enabled and clear for accurate voice recognition
   - Confirm Terraform and AWS CLI are correctly installed and accessible via your system PATH
   - Ansible is Linux-native:
      - Use WSL (Windows Subsystem for Linux) to run Ansible on Windows machines
      - On macOS/Linux, Ansible works natively without additional setup

## Features by Version
###  v1.0.0 – Initial Release
- Voice-to-text using `speech_recognition`
- Extracts key EC2 parameters from voice:
  - Instance type (e.g., t2.micro)
  - Region (e.g., ap-south-1)
  - Volume size (e.g., 10 GB)
- Generates `main.tf` dynamically from a backup template
- Runs `terraform init` and `terraform apply`

###  v1.0.1 – Destroy Feature Added
- Recognizes **destroy**, **terminate**, or **delete** keywords
- Prompts for **voice confirmation** before destruction
- Runs `terraform destroy` safely after "yes" is spoken
- Voice-controlled infrastructure teardown!

### v1.0.2 – Backend State Management
- Added backend state management using AWS S3 and DynamoDB
- Ensures safer state storage and collaboration
- Improved error handling and rollback support
- Code structure optimized for maintainability

### v1.0.3 – Full Infra Lifecycle & Voice-Controlled Cleanup
- Voice-Controlled EC2 Lifecycle
  - Create/destroy EC2 instances using natural speech
  - Detects instance type, region, and EBS volume size
- Dynamic Key Pair & SSH Access
  - Creates key pair only if SSH is requested
  - Saves .pem locally with secure permissions
  - Deletes AWS key and local PEM file during cleanup
 - Security Group Handling
   - Creates & attaches SSH-enabled SG if needed
 - Fuzzy Input Matching
   - Corrects misheard inputs (e.g., "a2micro" → t2.micro, "mumbai" → ap-south-1)
 - Safe Voice Confirmation for Destruction
   - Asks for "yes" before terraform destroy
 - Terraform Backend Cleanup
   - Deletes state file from S3 and lock from DynamoDB
   - Parses backend values from main.tf.backup to avoid hardcoding
 - Connection Output
   - Prints public IP and SSH command after creation
 - Idempotent Infra Handling
   - Avoids duplicate key/SG creation on re-run

### v1.0.4 – YAML-Based Infra + Ansible Automation
- Introduced Mode 2: YAML-driven infrastructure provisioning
- Supports:
  - Custom VPC and subnet creation via vpc_custom.yaml
  - EC2 instance + EBS volume provisioning via custom.yaml
  - Inline and file-based Security Group rule parsing
- Added objective: destroy support in YAML
- Integrated Ansible for post-creation configuration:
  - Converts Terraform state into inventory
  - Renders playbook from Jinja2 template
  - Runs remote config via SSH
- Fully modular architecture via modules/mode_1/custom/
- Jinja2-based templates for Terraform and Ansible
- Automatic AMI resolution (ami: auto)
- Terraform backend (S3 + DynamoDB) via backend.yaml

<p align="center">
  <img src="https://drive.google.com/uc?export=view&id=1JxOG1Vo1wXShL9yd1EAZlqYnTEGW6ezd" width="300" alt="Custom Screenshot or Output" />
</p>

## License
This project is for educational and prototype purposes only.
