resource "aws_iam_user" "redshift-user" {
  name = "${var.project_name}-redshift-user"
}

resource "aws_iam_access_key" "redshift-credentials" {
  user = aws_iam_user.redshift-user.name
}

resource "aws_secretsmanager_secret" "redshift-iam-secrets" {
  name                    = "${var.project_name}/${var.environment}/redshift-iam-user-credentials"
  description             = "IAM credentials for redshift user"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "redshift-secrets-version" {
  secret_id = aws_secretsmanager_secret.redshift-iam-secrets.id
  secret_string = jsonencode({
    assess_key = aws_iam_access_key.redshift-credentials.id
    secret_key = aws_iam_access_key.redshift-credentials.secret
  })
}

# Least privilege permission
resource "aws_iam_policy" "redshift-policy" {
  name        = "${var.project_name}-redshift-user-policy"
  description = "Permission policy for our redshift user"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "RedshiftS3Permissons"
        Effect   = "Allow",
        Action   = ["s3:GetObject", "s3:ListBucket", "s3:PutObject", "s3:DeleteObject"]
        Resource = ["arn:aws:s3:::github*"]
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "redshift-policy-attach" {
  user       = aws_iam_user.redshift-user.name
  policy_arn = aws_iam_policy.redshift-policy.arn
}