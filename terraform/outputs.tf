# outputs.tf — Informations affichées après terraform apply

output "vpc_id" {
  description = "ID du VPC créé"
  value       = aws_vpc.main.id
}

output "public_subnet_id" {
  description = "ID du sous-réseau public"
  value       = aws_subnet.public.id
}

output "ec2_standby_ip" {
  description = "IP publique de l'instance EC2 de secours"
  value       = aws_instance.standby.public_ip
}

output "ec2_standby_id" {
  description = "ID de l'instance EC2 de secours"
  value       = aws_instance.standby.id
}
