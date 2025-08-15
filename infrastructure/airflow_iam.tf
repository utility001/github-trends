# Airflow needs a user in order to be able to stage the raw api data in s3 bucket before further processing

resource "aws_iam_user" "airflow-user" {
  name = "${var.project_name}-airflow-user"
}

resource "aws_iam_access_key" "airflow-credentials" {
  user = aws_iam_user.airflow-user.name
}

resource "aws_secretsmanager_secret" "airflow-secrets" {
  name                    = "${var.project_name}/dev/airflow-user-creds"
  description             = "IAM credentials for our airflow user"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "airflow-secrets-version" {
  secret_id = aws_secretsmanager_secret.airflow-secrets.id
  secret_string = jsonencode({
    assess_key = aws_iam_access_key.airflow-credentials.id
    secret_key = aws_iam_access_key.airflow-credentials.secret
  })
}

# Least privilege permission
resource "aws_iam_policy" "airflow-policy" {
  name        = "${var.project_name}-airflow-user-policy"
  description = "Permission policy for our airflow user"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "WriteToBucket"
        Effect   = "Allow",
        Action   = ["s3:GetObject", "s3:ListBucket", "s3:PutObject"]
        Resource = ["arn:aws:s3:::github*"]
      },
    ]
  })
}

resource "aws_iam_user_policy_attachment" "airflow-policy-attach" {
  user       = aws_iam_user.airflow-user.name
  policy_arn = aws_iam_policy.airflow-policy.arn
}