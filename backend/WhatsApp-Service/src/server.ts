import express from "express";
import { connectDB } from "./config/db";
import waRouter from "./routes/webhook";
// port should be number type default is 8080
const PORT = process.env.PORT ? parseInt(process.env.PORT, 10) : 8080;
const app = express();
app.use(express.json()); // if using better-auth be careful

app.use("/webhook", waRouter);

app.listen(PORT, "0.0.0.0", async () => {
  console.log(`Server running on 0.0.0.0:${PORT}`);
  await connectDB(process.env.MONGO_URI!);
});
