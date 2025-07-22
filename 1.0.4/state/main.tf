terraform {
  backend "s3" {
    bucket         = "voiceiac-tf-state"
    key            = "ec2/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "voiceiac-tf-locks"
  }
}

provider "aws" {
  region = "us-east-1"
}


resource "aws_security_group" "custom_sg" {
  name        = "custom_sg"
  description = "Custom_SG_for_EC2"


  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }



}


resource "aws_instance" "myec2" {
  ami           = "ami-0871b7e0b83ae16c4"
  instance_type = "t2.micro"

  root_block_device {
    volume_size = 8
  }


  key_name = "voiceiac-key"



  vpc_security_group_ids = [

    aws_security_group.custom_sg.id

  ]


  tags = {
    Name = "voiceiac-instance"
  }
}

output "instance_ip" {
  value       = aws_instance.myec2.public_ip
  description = "The public IP of the EC2 instance"
}