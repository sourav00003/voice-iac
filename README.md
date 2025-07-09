# Voice-IaC – Voice Controlled Infrastructure as Code

Voice-IaC is a voice-controlled Infrastructure-as-Code (IaC) system built using Python and Terraform. It enables you to **create** or **destroy AWS EC2 instances** using simple spoken commands.

## Features

- Voice-to-Text using Google Speech Recognition
- Extracts key parameters: instance_type, region, volume_size, action
- Dynamically generates main.tf from a template
- Runs terraform init and apply programmatically
- Predefined support for AWS regions and EC2 instance types
- Destroy functionality planned for future version

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
2. The Python script extracts:
       Action: create / destroy
       Instance Type: t2.micro, t3a.small, etc.
       Region: us-east-1, ap-south-1, etc.
       Volume Size: 8, 10, etc.
3. Based on extracted data, main.tf is generated using main.tf.backup as a template.
4. Terraform commands (init, apply) are executed automatically.

## Tech Stack

| Layer        | Tools / Services                       |
|--------------|-----------------------------------------|
| Voice Input  | Python (SpeechRecognition, PyAudio)     |
| Processing   | normalization, keyword matching |
| IaC Engine   | Terraform (AWS Provider)               |
| Cloud Infra  | AWS (EC2, EBS)                         |
| Integration  | Python subprocess for Terraform        |

## Getting Started
## Prerequisites
- Python 3.x
- Terraform installed and in system PATH
- AWS CLI installed and configured with valid credentials
- Microphone enabled and working

## Python Dependencies

```bash
pip install SpeechRecognition
pip install pyaudio
```
## Example Voice Commands
- Create a t2.micro instance in ap-south-1 with 8GB
- Launch a t3.small instance in us-west-2 with 10GB
- Destroy instance in us-east-1 (feature coming soon)

##  Notes
- Only predefined EC2 instance types and AWS regions are supported in the current version.
- The destroy command functionality will be added in upcoming versions.
- Ensure Terraform is installed and available in your system's PATH.

## License
This project is for educational and prototype purposes only.


