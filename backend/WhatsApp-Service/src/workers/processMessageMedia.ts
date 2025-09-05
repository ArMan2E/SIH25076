import { Message } from "../model/MessageModel";
import { parseWhatsAppMessage } from "../util/whatsappParser";
import {
  getMediaUrlFromWhatsApp,
  uploadToS3FromUrl,
} from "../service/whatsAppMediaUrlGetService";

export async function processIncomingMessage(entry: any) {
  try {
    const parsedMessage = parseWhatsAppMessage(entry);
    let s3Key: string | undefined = undefined;
    if (!parsedMessage) {
      console.warn("Unknown message likely returning null from the parser");
    }
    console.log(parsedMessage);
    if (parsedMessage?.mediaId) {
      const mediaUrl = await getMediaUrlFromWhatsApp(parsedMessage.mediaId);
      const ext = parsedMessage.mimeType?.split("/")[1] || "bin"; // extension mostly jpeg, mp4, mp3
      s3Key = `media/${parsedMessage.mediaId}.${ext}`;
      await uploadToS3FromUrl(mediaUrl, s3Key);
    }

    const msg = new Message({
      waMessageId: parsedMessage?.id,
      from: parsedMessage?.from,
      type: parsedMessage?.type,
      body: parsedMessage?.body,
      caption: parsedMessage?.caption,
      mimeType: parsedMessage?.mimeType,
      mediaId: parsedMessage?.mediaId,
      s3Key,
      filename: parsedMessage?.filename,
      sha256: parsedMessage?.sha256,
      latitude: parsedMessage?.latitude,
      longitude: parsedMessage?.longitude,
      address: parsedMessage?.address,
      name: parsedMessage?.name,
      url: parsedMessage?.url,
      timestamp: parsedMessage?.timestamp
        ? new Date(+parsedMessage.timestamp * 1000)
        : new Date(),
      raw: parsedMessage?.raw,
    });

    await msg.save(); // monoose save to dbচ
    console.log("Message saved to db", msg.waMessageId);
  } catch (error) {
    console.error("Failed to process message...", error);
  }
}
