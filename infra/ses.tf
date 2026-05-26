resource "aws_ses_domain_identity" "bluepages" {
  domain = "bluepages.ecotrust.org"
}

resource "aws_ses_domain_dkim" "bluepages" {
  domain = aws_ses_domain_identity.bluepages.domain
}