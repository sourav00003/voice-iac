# Voice-IaC – Voice Controlled Infrastructure as Code

Voice-IaC is a voice-controlled Infrastructure-as-Code (IaC) system built using Python and Terraform. It enables you to **create** or **destroy AWS EC2 instances** using simple spoken commands.

## Features

- Converts speech to text using Python (SpeechRecognition)
- Extracts key parameters like instance type, region, volume size, and action (create/destroy)
- Generates `main.tf` file dynamically from a backup template
- Initializes and applies infrastructure using Terraform
- Outputs the public IP of the EC2 instance

## Tech Stack

| Layer        | Tools / Services                       |
|--------------|-----------------------------------------|
| Voice Input  | Python (SpeechRecognition, PyAudio)     |
| Processing   | Regex, normalization, keyword matching |
| IaC Engine   | Terraform (AWS Provider)               |
| Cloud Infra  | AWS (EC2, EBS)                         |
| Integration  | Python subprocess for Terraform        |

## Voice Command Examples

```text
Create a t2.micro instance in us-east-1 with 8GB volume
Launch a t3.micro instance in ap-south-1 with 10 GB
Terminate the iacvoice instance in us-east-1
