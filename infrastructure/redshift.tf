# PASSWORD AND SECRETS
resource "random_password" "redshift-password" {
  length           = 20
  override_special = "()!#$%&_+-={}|" # A list of special characters that will be used in creating the password
  special          = true
  numeric          = true
  upper            = true
  lower            = true
}

resource "aws_secretsmanager_secret" "redshift-db-admin-secrets" {
  name                    = "${var.project_name}/${var.environment}/redshift-db-admin-credentials"
  description             = "Database admin credentials for the redshift cluster"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "redshift_admin_secrets_version" {
  secret_id = aws_secretsmanager_secret.redshift-db-admin-secrets.id
  secret_string = jsonencode({
    username = "${var.project_name}-redshift-admin"
    password = random_password.redshift-password.result
  })
}


# SECURITY GROUP CONFIG
resource "aws_security_group" "redshift-security-group" {
  name   = "${var.project_name}-redshift-security-group"
  vpc_id = aws_vpc.vpc.id # Updated to match your VPC name
}

resource "aws_vpc_security_group_ingress_rule" "redshift-ingress-rule" {
  security_group_id = aws_security_group.redshift-security-group.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 5439
  to_port           = 5439
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "redshift-egress-rule" {
  security_group_id = aws_security_group.redshift-security-group.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

# SUBNET GROUP
resource "aws_redshift_subnet_group" "redshift-subnet-group" {
  name       = "${var.project_name}-${var.environment}-redshift-subnet-group"
  subnet_ids = [aws_subnet.public-subnet-a.id, aws_subnet.public-subnet-b.id]
}

# PARAMETER GROUP
resource "aws_redshift_parameter_group" "redshfit-param-group" {
  name   = "${var.project_name}-redshift-param-group"
  family = "redshift-2.0"

  parameter {
    name  = "require_ssl"
    value = "false"
  }
}

# REDSHIFT CLUSTER
resource "aws_redshift_cluster" "redshift_cluster" {
  cluster_identifier           = "${var.project_name}-${var.environment}-redshift-cluster"
  database_name                = "${var.redshift_warehouse_name}"
  master_username              = "${var.project_name}-redshift-admin"
  master_password              = random_password.redshift-password.result
  node_type                    = "ra3.large"
  cluster_type                 = "multi-node"
  number_of_nodes              = 2
  publicly_accessible          = true
  port                         = 5439
  encrypted                    = true
  cluster_subnet_group_name    = aws_redshift_subnet_group.redshift-subnet-group.name
  vpc_security_group_ids       = [aws_security_group.redshift-security-group.id]
  skip_final_snapshot          = true
  cluster_parameter_group_name = aws_redshift_parameter_group.redshfit-param-group.name
}