terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" { region = var.aws_region }

resource "aws_s3_bucket" "migration_staging" {
  bucket = "${var.environment}-migration-staging-${var.aws_account_id}"
}

resource "aws_glue_catalog_database" "migration_catalog" {
  name = "${var.environment}_enterprise_migration_db"
}
