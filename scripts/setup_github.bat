@echo off
setlocal
echo ===================================================
echo  Enterprise Cloud Data Migration Platform
echo ===================================================
git init
git branch -M main
git add .
git commit -m "feat: Enterprise Cloud Data Migration & Modern ELT Platform - AWS S3, Glue, Redshift, dbt Core, Terraform"
set /p GH_USER="Enter GitHub username (or press enter for soniablaketech/masonmirtech): "
git remote remove origin 2>nul
git remote add origin https://github.com/%GH_USER%/enterprise-cloud-data-migration.git
git push -u origin main
pause
