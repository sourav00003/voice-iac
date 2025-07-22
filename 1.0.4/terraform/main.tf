# Terraform backend configuration
terraform {
  backend "s3" {
    bucket         = "customiac"
    key            = "custom/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "custom-tf-locks"
  }
}

# AWS Provider
provider "aws" {
  region = "us-east-1"
}

# VPC Resource
resource "aws_vpc" "custom_vpc" {
  cidr_block           = "172.31.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "default-like-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.custom_vpc.id
  tags = {
    Name = "igw-default-like-vpc"
  }
}

# Route Table
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.custom_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  tags = {
    Name = "public-rt-default-like-vpc"
  }
}

# Subnets and Route Table Associations

resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.custom_vpc.id
  cidr_block              = "172.31.0.0/20"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true
  tags = {
    Name = "public_a"
  }
}

resource "aws_route_table_association" "public_a_assoc" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_subnet" "public_b" {
  vpc_id                  = aws_vpc.custom_vpc.id
  cidr_block              = "172.31.16.0/20"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true
  tags = {
    Name = "public_b"
  }
}

resource "aws_route_table_association" "public_b_assoc" {
  subnet_id      = aws_subnet.public_b.id
  route_table_id = aws_route_table.public_rt.id
}


# Security Group
resource "aws_security_group" "custom_sg" {
  name        = "custom_sg"
  description = "Custom_SG_for_EC2"
  vpc_id      = aws_vpc.custom_vpc.id


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




  egress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }


}


# EC2 Instances

resource "aws_instance" "app-server-1" {
  ami                    = "ami-0871b7e0b83ae16c4"
  instance_type          = "t2.micro"
  key_name               = "custom-key"
  count                  = 2
  subnet_id              = aws_subnet.public_a.id
  vpc_security_group_ids = [aws_security_group.custom_sg.id]

  root_block_device {
    volume_size = 8
    volume_type = "gp2"
  }

  tags = {
    Name = "app-server-1-${count.index}"
  }
}

resource "aws_instance" "app-server-2" {
  ami                    = "ami-0871b7e0b83ae16c4"
  instance_type          = "t2.micro"
  key_name               = "custom-key"
  count                  = 2
  subnet_id              = aws_subnet.public_b.id
  vpc_security_group_ids = [aws_security_group.custom_sg.id]

  root_block_device {
    volume_size = 8
    volume_type = "gp3"
  }

  tags = {
    Name = "app-server-2-${count.index}"
  }
}
