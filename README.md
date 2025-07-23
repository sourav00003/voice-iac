# Voice-IaC – Voice Controlled Infrastructure as Code

Voice-IaC is a voice-controlled Infrastructure-as-Code (IaC) system built using Python and Terraform. It enables you to **create** or **destroy AWS EC2 instances** using simple spoken commands.

## Features

- Voice-to-Text using Google Speech Recognition
- Extracts key parameters: instance_type, region, volume_size, action
- Dynamically generates main.tf from a template
- Runs terraform init and apply programmatically
- Predefined support for AWS regions and EC2 instance types
- Adds optional SSH access with key pair and security group
- Uses S3 for backend state storage and DynamoDB for state locking
- Cleans up: destroys infra, deletes S3 state file, removes DynamoDB lock, deletes local/private key


## Project Structure
```bash
1.0.4/
├── ansible/
│   ├── modules/
│   └── playbook/
│       ├── inventory.yaml             # Generated from TF state
│       └── site.yaml                  # Rendered Ansible playbook
├── backend/
│   └── backend.yaml                   # S3 + DynamoDB backend config
├── modules/
│   ├── ec2_custom_generator.py        # Generates main.tf from YAML (Mode 2)
│   ├── ec2_generator.py               # Used in Mode 1 (default VPC)
│   ├── sg_generator.py                # (Legacy/global SG parser)
│   ├── template_parser.py             # Parses custom.yaml for Mode 2
│   ├── terraform_runner.py            # (Used for Mode 1)
│   ├── utils/
│   │   └── file_finder.py             # Utility for finding config/template files
│   └── mode_1/
│       ├── fetchami.py                # Fetches latest AMI ID (Amazon Linux 2)
│       └── custom/
│           ├── aws_utils.py              # Manages key pair, subnet/VPC fetch
│           ├── complete_parser.py        # Parses all YAMLs + SG + backend + VPC
│           ├── ec2_only_generator.py     # For Option 1 & 2 (default/existing VPC)
│           ├── vpc_ec2_generator.py      # For Option 3 (custom VPC + EC2s)
│           ├── sg_generator.py           # Parses `custom_sg_rules.txt`
│           ├── vpc_checker.py            # Validates if a VPC ID exists in AWS
│           └── main_generator.py         # (May orchestrate Mode 1 from YAML)
├── templates/
│   ├── main.tf.j2                    # Template for EC2-only TF (default/existing VPC)
│   ├── vpc_ec2.tf.j2                 # Template for full infra with custom VPC
│   └── playbook.j2                   # Template for Ansible playbook (site.yaml)
├── yaml/
│   ├── custom.yaml                   # User-defined infra config (instances, VPC, SG)
│   ├── vpc_custom.yaml               # Custom VPC and subnet config
│   └── custom_ansible.yaml           # Post-provision Ansible tasks
├── main.py                           # Entry point (asks for Mode 1 or Mode 2)
├── mode1_handler.py                  # Handles Mode 1 (voice-based provisioning)
├── mode2_handler.py                  # Handles Mode 2 (YAML-based provisioning)
├── terraform_runner2.py              # Executes Terraform for Mode 2
├── custom_sg_rules.txt               # Optional SG rule file used in YAML SG creation
├── test.py                           # Script to test SG parsing logic
```
## How It Works
1. User speaks a natural language command:
   Create a t2.micro instance in us-east-1 with 8GB volume
   or
   Destroy the Infrastructure
2. The Python script extracts the following from your voice:
       Action: create / destroy
       Instance Type: t2.micro, t3a.small, etc.
       Region: us-east-1, ap-south-1, etc. (with fuzzy matching)
       Volume Size: 8, 10, etc.
3. main.tf is generated dynamically using main.tf.backup as a template.
   - Adds optional SSH access based on user input
   - Injects key pair and security group blocks if needed
4. Terraform commands are executed:
   - terraform init
   - terraform apply (for creation)
   - terraform destroy (for teardown after confirmation)
5. On destroy, it also:
   - Deletes EC2 instance and security group
   - Removes the S3 state file
   - Deletes the lock from DynamoDB
   - Deletes AWS key pair and local .pem file

## Tech Stack

| Layer        | Tools / Services                       |
|--------------|-----------------------------------------|
| Voice Input  | Python (SpeechRecognition, PyAudio)     |
| Processing   | Normalization, Fuzzy Matching, Regex-based Keyword Extraction |
| IaC Engine   | Terraform (AWS Provider, Backend: S3 + DynamoDB)               |
| Cloud Infra  | AWS (EC2, EBS, Security Group, Key Pair)                         |
| Integration  | Python subprocess, boto3 for AWS resource handling        |
| State Backend  | S3 (Terraform state) + DynamoDB (state locking)        |

## Getting Started
## Prerequisites
- Python 3.x installed (recommended: 3.8+)
- Terraform CLI installed and added to your system’s PATH
- AWS CLI installed and configured with valid credentials (aws configure)
- Microphone enabled and working (for voice input)
- AWS Account with permissions to:
  - Launch/terminate EC2 instances
  - Create/delete key pairs and security groups
  - Create and manage S3 buckets (for storing Terraform state)
  - Create and manage DynamoDB tables (for state locking)

## Python Dependencies

```bash
pip install SpeechRecognition
pip install pyaudio
pip install boto3
```
## Example Voice Commands
## Create Commands
  - Create a t2.micro instance in ap-south-1 with 8GB
  - Launch a t3.small instance in us-west-2 with 10GB
  - Destroy instance in us-east-1 (From V1.0.1)
## Destroy Commands
  - Destroy the infrastructure
  - Terminate the EC2 instance in us-east-1
  - Delete all

##  Notes
- Only predefined EC2 instance types and AWS regions are supported (more can be added later).
- Voice-based destroy functionality is fully supported from v1.0.1+.
- Backend state is managed via S3 and DynamoDB (from v1.0.2).
- The system intelligently handles fuzzy voice inputs like "t2mic" → "t2.micro" or "Mumbai" → "ap-south-1".
- Ensure microphone access is granted and audio is clear for accurate voice recognition.
- Make sure Terraform and AWS CLI are installed and properly configured in your system's PATH.

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

## License
This project is for educational and prototype purposes only.
