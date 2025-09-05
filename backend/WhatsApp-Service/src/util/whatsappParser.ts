import type { ParsedMessage } from "../types/message";

export function parseWhatsAppMessage(message: any): ParsedMessage | null {
  const base: ParsedMessage = {
    type: message.type,
    id: message.id, // whats app message id
    from: message.from,
    timestamp: message.timestamp,
    raw: message,
  };

  switch (message.type) {
    /**
     * https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/reference/messages/audio
     * https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/reference/messages/image
     * https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/reference/messages/video
     * above links describes the payload structure
     * message array have the media details under their respective types hence message[message.type]
     * another way for property access
     * if message.type is "image", then message[message.type] is message.image.
     * not hardcoding image/video/audio cause redundant code needs to be written
     */
    case "image":
    case "video":
    case "audio":
      return {
        ...base,
        caption: message[message.type]?.caption,
        mimeType: message[message.type]?.mime_type,
        sha256: message[message.type]?.sha256,
        mediaId: message[message.type]?.id,
      };
    //https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/reference/messages/document
    // here hardcoding message.document cause single case
    case "document":
      return {
        ...base,
        caption: message.document?.caption,
        filename: message.document?.filename,
        mediaId: message.document?.id,
        mimeType: message.document?.mime_type,
        sha256: message.document?.sha256,
      };
    case "location":
      return {
        ...base,
        latitude: message.location?.latitude,
        longitude: message.location?.longitude,
        name: message.location?.name,
        url: message.location?.url,
        address: message.location?.address,
      };
    case "text":
      return {
        ...base,
        body: message.text?.body,
      };
    default:
      return null;
  }
}
