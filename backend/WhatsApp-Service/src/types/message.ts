export interface ParsedMessage {
  type: "text" | "image" | "audio" | "video" | "location" | "document";

  // common message body
  from?: string;
  id?: string;
  timestamp?: string;
  // text message type
  body?: string;
  // media, can be used for document document.id -> mediaId
  mediaId?: string; // mandatory to download the file from meta server
  caption?: string;
  mimeType?: string;

  // document type
  filename?: string;
  sha256?: string;

  // location
  latitude?: number;
  longitude?: number;
  address?: string; // location address
  name?: string; // location name
  url?: string;
  // fallback
  raw?: any;
}
