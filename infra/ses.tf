resource "aws_ses_domain_identity" "bluepages" {
  domain = "bluepages.ecotrust.org"
}

resource "aws_ses_domain_dkim" "bluepages" {
  domain = aws_ses_domain_identity.bluepages.domain
}

resource "aws_ses_domain_mail_from" "bluepages" {
  domain           = aws_ses_domain_identity.bluepages.domain
  mail_from_domain = "noreply.${aws_ses_domain_identity.bluepages.domain}"
}