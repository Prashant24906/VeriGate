import { MongoClient, Db } from "mongodb";

const uri = process.env.MONGODB_URI || "";
const DB_NAME = "verigate";

if (!uri) {
  console.warn(
    "[VeriGate] MONGODB_URI is not set in .env.local. " +
    "MongoDB features (audit log, dashboard) will be disabled."
  );
}

// Use a cached client in development to avoid creating new connections on every hot reload
let client: MongoClient | null = null;
let db: Db | null = null;

export async function getDb(): Promise<Db | null> {
  if (!uri) return null;

  if (db) return db;

  try {
    client = new MongoClient(uri);
    await client.connect();
    db = client.db(DB_NAME);
    console.log("[VeriGate] Connected to MongoDB:", DB_NAME);
    return db;
  } catch (err) {
    console.error("[VeriGate] MongoDB connection failed:", err);
    return null;
  }
}

export const COLLECTIONS = {
  screenings: "screenings",
} as const;
