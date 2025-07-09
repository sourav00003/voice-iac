terraform {
  backend "s3" {
    bucket         = "voiceiac-tf-state"
    key            = "ec2/terraform.tfstate"
    region         = "us-east-1" # Region where the bucket exists
    encrypt        = true
    dynamodb_table = "voiceiac-tf-locks" # DynamoDB table for state locking
  }
}

provider "aws" {
  region = "us-east-1"

}
data "aws_vpc" "default" {
  default = true
}


resource "aws_security_group" "ssh_sg" {
  name        = "ssh_sg"
  description = "Allow SSH"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "ssh-sg"
  }
}


resource "aws_instance" "voice_instance" {
  ami           = "ami-05ffe3c48a9991133"
  instance_type = "t2.micro"
  key_name      = "voiceiac-key"

  root_block_device {
    volume_size = 8
  }

  vpc_security_group_ids = [aws_security_group.ssh_sg.id]

  tags = {
    Name = "iacvoice"
  }
}

output "instance_ip" {
  value       = aws_instance.voice_instance.public_ip
  description = "The public IP of the EC2 instance"
}
