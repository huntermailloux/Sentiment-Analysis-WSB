import { MongoClient } from "mongodb";

const MONGO_URI = process.env.MONGODB_URI;
const DB_NAME = "sentiment-analysis";

export default async function handler(req, res) {
  if (req.method !== "GET") {
    return res.status(405).json({ error: "Method Not Allowed" });
  }

  try {
    const client = await MongoClient.connect(MONGO_URI);
    const db = client.db(DB_NAME);
    
    const posts = await db.collection("posts").find({}).toArray();

    client.close();

    return res.status(200).json({ posts });
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
}
