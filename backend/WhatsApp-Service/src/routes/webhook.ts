import express from "express";
import {
  handleIncomingMessage,
  verifyWebhook,
} from "../controllers/messageController";

const waRouter = express.Router();

// webhook verification / get
waRouter.get("/", verifyWebhook);

// incoming message POST
waRouter.post("/", handleIncomingMessage);

export default waRouter;
