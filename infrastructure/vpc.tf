# vpc
resource "aws_vpc" "vpc" {
  cidr_block = "10.11.0.0/16"

  # RDS needs dns support and dns hostnames
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

# IGW
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc.id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

# Public subnet -- RDS needs at least two subnets in its subnet group
resource "aws_subnet" "public-subnet-a" {
  vpc_id            = aws_vpc.vpc.id
  cidr_block        = "10.11.0.0/24"
  availability_zone = "eu-north-1a"

  tags = {
    Name = "${var.project_name}-pub-subnet-a"
  }
}

resource "aws_subnet" "public-subnet-b" {
  vpc_id            = aws_vpc.vpc.id
  cidr_block        = "10.11.1.0/24"
  availability_zone = "eu-north-1b"

  tags = {
    Name = "${var.project_name}-pub-subnet-b"
  }
}

resource "aws_route_table" "public-route-table" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "${var.project_name}-pub-route-table"
  }
}

resource "aws_route_table_association" "pub_rt_assoc_a" {
  subnet_id      = aws_subnet.public-subnet-a.id
  route_table_id = aws_route_table.public-route-table.id
}

resource "aws_route_table_association" "pub_rt_assoc_b" {
  subnet_id      = aws_subnet.public-subnet-b.id
  route_table_id = aws_route_table.public-route-table.id
}
