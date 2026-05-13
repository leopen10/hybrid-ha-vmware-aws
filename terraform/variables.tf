# variables.tf — Variables du projet

variable "aws_region" {
  description = "Région AWS"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR du VPC AWS"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR du sous-réseau public"
  type        = string
  default     = "10.0.1.0/24"
}

variable "private_subnet_cidr" {
  description = "CIDR du sous-réseau privé"
  type        = string
  default     = "10.0.2.0/24"
}

variable "onprem_cidr" {
  description = "CIDR autorisé pour SSH"
  type        = string
  default     = "0.0.0.0/0"
}

variable "ami_id" {
  description = "AMI Ubuntu 22.04 us-east-1"
  type        = string
  default     = "ami-0c7217cdde317cfec"
}

variable "instance_type" {
  description = "Type d'instance EC2"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "Nom de la clé SSH AWS"
  type        = string
  default     = "hybrid-ha-key"
}
