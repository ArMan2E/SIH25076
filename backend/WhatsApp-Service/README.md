# WhatsApp Service

## Setup Environment Variables

Create a `.env` file in this dir:

```env
# WhatsApp / Meta
WA_TOKEN=
PHONE_NO_ID=
WAPB_ID=
# VERIFY_TOKEN (important)
WA_VERIFY_TOKEN=secretkey
WA_BASE_URL=https://graph.facebook.com
WA_GRAPH_VERSION=v23.0

# MongoDB
MONGO_DB_NAME=krishi
MONGO_URI=

# AWS
AWS_REGION=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET=
```

---

## Terraform Infrastructure

1. Create a `.tfvars` file with environment-specific variables.
2. Run the following Terraform commands:

```bash
terraform init
terraform plan -out=<planname>.plan -var-file="var.tfvars"
terraform apply "<planname>.plan"
```

- To destroy the infrastructure:

```bash
terraform destroy
```

---

## Docker & Deployment

1. Build the Docker image:

```bash
docker-compose build
```

2. Tag and push the Docker image to Docker Hub:

```bash
docker tag <imgname>:latest <dockerhub>/<imgname>:latest
docker push <dockerhub>/<imgname>:latest
```

3. Deploy the image in **Render** (or your preferred cloud provider).

4. Register the **webhook URL** of your Render deployment in the **Meta Business Manager Dashboard**.

5. Make sure to obtain the **permanent access token** from Meta (refer to their documentation).

---

## Notes

- Always respond with `200 OK` from your webhook to avoid retries from WhatsApp
- then go on about the async task
- rn async is good no need for queue model like kafka/ SQS
