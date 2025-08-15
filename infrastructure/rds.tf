# Redshift security group
resource "aws_security_group" "rds-security-group" {
  name        = "${var.project_name}-security-group"
  description = "Security Group"
  vpc_id      = aws_vpc.vpc.id
}

resource "aws_vpc_security_group_ingress_rule" "rds-ingress-rule" {
  security_group_id = aws_security_group.rds-security-group.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 5432
  ip_protocol       = "tcp"
  to_port           = 5432
}

resource "aws_vpc_security_group_egress_rule" "rds-egress-rule" {
  security_group_id = aws_security_group.rds-security-group.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

# RDS subnet group
resource "aws_db_subnet_group" "rds-subnet-group" {
  name = "${var.project_name}-rds-subnet-group"
  subnet_ids = [
    aws_subnet.public-subnet-a.id,
    aws_subnet.public-subnet-b.id
  ]
}

resource "random_password" "rds-password" {
  length           = 16
  override_special = "()!#$%&_+-={}|"
  special          = true
  numeric          = true
  upper            = true
  lower            = true
}

resource "aws_secretsmanager_secret" "rds-admin-secrets" {
  name                    = "${var.project_name}/${var.environment}/rds-db-admin-credentials/"
  description             = "Database Admin credentials for the rds cluster"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "rds-admin-secrets-version" {
  secret_id = aws_secretsmanager_secret.rds-admin-secrets.id
  secret_string = jsonencode({
    username = "${var.project_name}_rds_admin"
    password = random_password.rds-password.result
  })
}

resource "aws_db_parameter_group" "rds-param-group" {
  name        = "${var.project_name}-rds-parameter-group"
  family      = "postgres16"
  description = "Disable SSL"

  parameter {
    name         = "rds.force_ssl"
    value        = "0"
    apply_method = "immediate"
  }
}

resource "aws_db_instance" "rds-instance" {
  identifier              = "${var.project_name}-db-instance"
  username                = "${var.project_name}_rds_admin"
  password                = random_password.rds-password.result
  engine                  = "postgres"
  engine_version          = "16.4"
  instance_class          = "db.m5.large"
  db_name                 = "${var.rds_db_name}"
  port                    = 5432
  publicly_accessible     = true
  allocated_storage       = 30
  apply_immediately       = true
  backup_retention_period = 0
  deletion_protection     = false
  skip_final_snapshot     = true
  parameter_group_name    = aws_db_parameter_group.rds-param-group.name
  vpc_security_group_ids  = [aws_security_group.rds-security-group.id]
  db_subnet_group_name    = aws_db_subnet_group.rds-subnet-group.name
}