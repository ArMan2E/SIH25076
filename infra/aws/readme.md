create .tfvar file and put bucket_name= "..."
terraform plan -out=tfplan1.plan -var-file="variables.tfvars"
