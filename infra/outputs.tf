output "ec2_public_ip" {
  description = "Elastic IP of the EC2 instance — use this for DNS and GitHub secrets"
  value       = aws_eip.bluepages.public_ip
}

output "ses_domain_records"{
  description = "DNS records to verify SES domain identity (add to Route53 or your DNS provider)"
  value = aws_ses_domain_identity.bluepages.verification_token
}