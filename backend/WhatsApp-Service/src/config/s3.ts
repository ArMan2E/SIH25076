import { S3Client } from "bun";

export const s3 = new S3Client({
  endpoint: process.env.AWS_S3_ENDPOINT || undefined,
  region: process.env.AWS_REGION!,
  accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  bucket: process.env.AWS_S3_BUCKET!,
});
