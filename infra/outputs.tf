output "ec2_public_ip" {
  description = "Elastic IP of the EC2 instance — use this for DNS and GitHub secrets"
  value       = aws_eip.bluepages.public_ip
}
