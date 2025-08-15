terraform {
  backend "s3" {
    bucket = "github-trends-infrastructure"
    key    = "dev/terraform.tfstate"
    region = "eu-north-1"
  }
}