param([string]$Username = "masonmirtech")
git init; git branch -M main; git add .
git commit -m "feat: Enterprise Cloud Data Migration & Modern ELT Platform - AWS S3, Glue, Redshift, dbt Core, Terraform"
git remote remove origin 2>$null
git remote add origin "https://github.com/$Username/enterprise-cloud-data-migration.git"
git push -u origin main
