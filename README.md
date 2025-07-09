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
voice-iac/
└── 1.0.0/
    ├── voice.py               # Main Python script
    ├── main.tf.backup         # Terraform template with placeholders
    ├── main.tf                # Auto-generated Terraform config
    ├── .gitignore             # Ignore Terraform and Python cache files
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

## License
This project is for educational and prototype purposes only.
