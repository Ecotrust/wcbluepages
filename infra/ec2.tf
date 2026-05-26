resource "aws_key_pair" "bluepages" {
  key_name   = "${var.project_name}-key"
  public_key = var.ssh_public_key

  tags = {
    Project = "${var.project_name}-production"
  }
}

resource "aws_instance" "bluepages" {
  ami                         = var.ec2_ami
  instance_type               = var.ec2_instance_type
  key_name                    = aws_key_pair.bluepages.key_name
  vpc_security_group_ids      = [aws_security_group.bluepages.id]
  iam_instance_profile        = aws_iam_instance_profile.bluepages.name
  subnet_id                   = tolist(data.aws_subnets.default.ids)[0]
  user_data_replace_on_change = true

  # TODO: add user_data script
  # Install Docker, AWS CLI v2, and git on first boot
  user_data = templatefile("user_data.tftpl", {
    aws_region           = var.aws_region
    web_ghcr_image_uri   = var.web_ghcr_image_uri
    django_secret_key    = var.django_secret_key
    sql_host             = var.sql_host
    sql_db_name          = var.sql_db_name
    sql_db_user          = var.sql_db_user
    sql_db_password      = var.sql_db_password
    sql_port             = var.sql_port
    django_allowed_hosts = var.django_allowed_hosts
    db_dump_file_path    = var.db_dump_file_path
    domain_name          = var.domain_name
    ssl_admin_email      = var.ssl_admin_email
    csrf_trusted_origins = var.csrf_trusted_origins
    email_host           = var.email_host
    email_host_user      = var.email_host_user
    email_host_password  = var.email_host_password
  })

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  tags = {
    Name    = "${var.project_name}-production-server"
    Project = var.project_name
  }
}

# Elastic IP so the address never changes across stop/start
resource "aws_eip" "bluepages" {
  instance = aws_instance.bluepages.id
  domain   = "vpc"

  tags = {
    Name    = "${var.project_name}-production-eip"
    Project = var.project_name
  }
}