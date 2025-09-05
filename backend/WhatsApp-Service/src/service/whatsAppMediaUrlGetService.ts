import { fetch } from "bun";
import { s3 } from "../config/s3";
const WA_TOKEN = process.env.WA_TOKEN!;
const WHATSAPP_API = `${process.env.WA_BASE_URL}/${process.env.WA_GRAPH_VERSION}`;

export async function getMediaUrlFromWhatsApp(
  mediaId: string
): Promise<string> {
  const res = await fetch(`${WHATSAPP_API}/${mediaId}`, {
    headers: { Authorization: `Bearer ${WA_TOKEN}` },
  });
  if (!res.ok) {
    throw new Error(`failed to get media url: ${res.statusText}`);
  }
  const data = (await res.json()) as { url: string };
  console.log(`url of media storage : ${data.url}`)
  return data.url;
}

export async function uploadToS3FromUrl(
  mediaUrl: string,
  key: string
): Promise<string> {
  const res = await fetch(mediaUrl, {
    headers: { Authorization: `Bearer ${WA_TOKEN}` },
  });
  if (!res.ok || !res.body) {
    throw new Error(`Failed to fetch media from MEta ${res.statusText}`);
  }
  // here key is the path in the bucket

  const s3WAFile = s3.file(key);
  try {
    const writer = s3WAFile.writer();
    for await (const chunk of res.body) {
      writer.write(chunk);
    }
    await writer.end();
  } catch (error) {
    console.error("Media not uploaded...");
  }
  return key;
}
