import type { Request, Response } from "express";
import { parseWhatsAppMessage } from "../service/whatsappParser";
// code written in the documentation only
export const verifyWebhook = (req: Request, res: Response) => {
  const hubMode = req.query["hub.mode"];
  const token = req.query["hub.verify_token"];
  const challange = req.query["hub.challange"];

  if (hubMode === "subscribe" && token === process.env.WA_VERIFY_TOKEN) {
    console.log("Webhook verified....");
    res.status(200).send(challange);
  } else {
    res.sendStatus(403);
  }
};

/**
 * https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/payload-examples
 * goto this link and se the dummy payload which is sent when user sends a message to the
 * webhook url
 * need to parse it properly , here using option chaining
 * the func is async as later on the parsed message is sent to db and obj storage
 *  according to the type field in the payload
 *
 *
 */
export const handleIncomingMessage = async (req: Request, res: Response) => {
  try {
    // req.body is the sent body, the json have "entry" array of size 1
    // hence check whether "entry" exists then move to ?.[0]
    // if that exist go to "changes" array of size 1 if changes exists goto fisrt idx
    // "value" obj have "messages" array of size 1 if "messages" exists go to 1st idx
    // THIS IS NECESSARY CAUSE WAP webhook MIGHT RETURN SENT/ DELIVERED events WHICH IS UNNECESSARY TO ME
    // JUST WANT THE MESSAGE,
    const entry = req.body?.entry?.[0]?.changes?.[0]?.value?.messages?.[0];
    // cause wap webhook sents different events treating them as wrong leads
    // wap to sent again causing api error
    // instead of treating as error gracefuly says response is received ot meta
    if (!entry) return res.sendStatus(200);

    //
    const parsedMessage = parseWhatsAppMessage(entry);
    console.log(parsedMessage); // rn console.
  } catch (error) {
    console.error("Error handling the payload", error);
    res.sendStatus(500); // cause it is my server hence 500 not metas error
  }
};
