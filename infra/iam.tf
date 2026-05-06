resource "aws_iam_role" "bluepages_ec2" {
  name = "${var.project_name}-ec2-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "bluepages_s3_read" {
  role = aws_iam_role.bluepages_ec2.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject"]
        Resource = "arn:aws:s3:::blue-pages-db-dump/*"
      },
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = "arn:aws:s3:::blue-pages-db-dump"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "bluepages" {
  name = "bluepages-ec2-profile"
  role = aws_iam_role.bluepages_ec2.name
}