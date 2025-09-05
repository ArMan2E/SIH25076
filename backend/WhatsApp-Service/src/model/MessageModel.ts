import mongoose, { Schema, Document } from "mongoose";

export interface WAPMessage extends Document {
  waMessageId: string;   // WhatsApp’s unique message id (wamid.xxxxx)
  from: string;
  type: string;

  body?: string;         // text body
  caption?: string;
  mimeType?: string;
  mediaId?: string;
  s3Key?: string;

  filename?: string;     // for documents
  sha256?: string;       // for documents

  latitude?: number;     // for location
  longitude?: number;
  address?: string;
  name?: string;
  url?: string;

  timestamp: Date;
  raw?: any;             // optional,
}

const MessageSchema = new Schema<WAPMessage>(
  {
    waMessageId: { type: String, required: true, unique: true },
    from: { type: String, required: true },
    type: { type: String, required: true },

    body: { type: String },
    caption: { type: String },
    mimeType: { type: String },
    mediaId: { type: String },
    s3Key: { type: String },

    filename: { type: String },
    sha256: { type: String },

    latitude: { type: Number },
    longitude: { type: Number },
    address: { type: String },
    name: { type: String },
    url: { type: String },

    timestamp: { type: Date, default: Date.now },
    raw: { type: Schema.Types.Mixed },
  },
  { timestamps: true }
);

export const Message = mongoose.model<WAPMessage>("wapMessage", MessageSchema);
