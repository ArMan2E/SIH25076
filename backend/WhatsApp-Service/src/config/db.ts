import mongoose from "mongoose";

export async function connectDB(uri: string) {
  try {
    await mongoose.connect(uri);
    console.log("MongoDb connected....");
  } catch (error) {
    console.error("Mongodb connection error", error);
    throw new Error("Connection error.. to mongodb");
  }
}
