import { NextRequest, NextResponse } from "next/server";
import { getDb, COLLECTIONS } from "@/lib/mongodb";

// GET /api/screenings/[id] — fetch a single screening from MongoDB
export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const db = await getDb();

    if (!db) {
      return NextResponse.json({ error: "MongoDB not configured" }, { status: 503 });
    }

    const doc = await db
      .collection(COLLECTIONS.screenings)
      .findOne({ screening_id: id });

    if (!doc) {
      return NextResponse.json({ error: "Screening not found" }, { status: 404 });
    }

    return NextResponse.json(doc);
  } catch (err) {
    console.error("[VeriGate] Failed to fetch screening by ID:", err);
    return NextResponse.json({ error: String(err) }, { status: 500 });
  }
}
