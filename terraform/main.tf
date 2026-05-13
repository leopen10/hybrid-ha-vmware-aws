# main.tf — Infrastructure hybride HA

# ─── VPC PRINCIPAL ───────────────────────────────────────────────
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "hybrid-ha-vpc"
    Project     = "hybrid-ha-vmware-aws"
    Environment = "production"
  }
}

# ─── SOUS-RÉSEAU PUBLIC ──────────────────────────────────────────
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidr
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "hybrid-ha-public-subnet"
    Type = "public"
  }
}

# ─── SOUS-RÉSEAU PRIVÉ ───────────────────────────────────────────
resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidr
  availability_zone = "${var.aws_region}a"

  tags = {
    Name = "hybrid-ha-private-subnet"
    Type = "private"
  }
}

# ─── INTERNET GATEWAY ────────────────────────────────────────────
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "hybrid-ha-igw"
  }
}

# ─── TABLE DE ROUTAGE PUBLIQUE ───────────────────────────────────
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "hybrid-ha-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# ─── SECURITY GROUP ──────────────────────────────────────────────
resource "aws_security_group" "ec2_sg" {
  name        = "hybrid-ha-ec2-sg"
  description = "Security group pour instances EC2 de secours"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "SSH depuis on-prem"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.onprem_cidr]
  }

  ingress {
    description = "Prometheus Node Exporter"
    from_port   = 9100
    to_port     = 9100
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "hybrid-ha-ec2-sg"
  }
}

# ─── INSTANCE EC2 DE SECOURS ─────────────────────────────────────
resource "aws_instance" "standby" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]
  key_name               = var.key_name

  tags = {
    Name    = "hybrid-ha-standby-01"
    Role    = "standby"
    Project = "hybrid-ha-vmware-aws"
  }
}
