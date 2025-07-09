terraform {
  backend "s3" {
    bucket         = "voiceiac-tf-state"        
    key            = "ec2/terraform.tfstate"    
    region         = "us-east-1"                #  Region where the bucket exists
    encrypt        = true
    dynamodb_table = "voiceiac-tf-locks"        #  DynamoDB table for state locking
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "voice_instance" {
  ami           = "ami-05ffe3c48a9991133"
  instance_type = "t2.micro"

  root_block_device {
    volume_size = 8
  }

  tags = {
    Name = "iacvoice"
  }
}

output "instance_ip" {
  value = aws_instance.voice_instance.public_ip
  description = "The public IP of the EC2 instance"
}