terraform {
  required_version = "~> 1.13.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 6.0" }
  }
  # Configure using -backend-config=backend.hcl; state bucket must exist first.
  backend "s3" {}
}
provider "aws" {
  region = var.region
  default_tags { tags = { Project = "ApplyTrail", ManagedBy = "Terraform" } }
}
