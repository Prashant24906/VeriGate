import { NextRequest, NextResponse } from "next/server";
import { getDb, COLLECTIONS } from "@/lib/mongodb";
import type { ScreeningResult } from "@/lib/api";

// POST /api/screenings — save a screening result to MongoDB
export async function POST(req: NextRequest) {
  try {
    const body: ScreeningResult = await req.json();
    const db = await getDb();

    if (!db) {
      // MongoDB not configured — silently succeed (screening still works without DB)
      return NextResponse.json({ ok: true, stored: false, reason: "MongoDB not configured" });
    }

    const doc = {
      ...body,
      _savedAt: new Date().toISOString(),
      // Flatten key fields for easy querying
      _riskLevel: body.risk_assessment?.risk_level,
      _riskScore: body.risk_assessment?.overall_risk_score,
      _recommendation: body.risk_assessment?.recommendation,
      _passportNumber: (body.document as Record<string, unknown>)?.passport_number,
      _holderName: (body.document as Record<string, unknown>)?.name,
      _tampered: body.tampering?.tampered,
      _faceMatch: body.face_verification?.match,
    };

    await db.collection(COLLECTIONS.screenings).insertOne(doc);

    return NextResponse.json({ ok: true, stored: true, screening_id: body.screening_id });
  } catch (err) {
    console.error("[VeriGate] Failed to save screening:", err);
    return NextResponse.json({ ok: false, error: String(err) }, { status: 500 });
  }
}

// GET /api/screenings?limit=20 — fetch recent screenings from MongoDB
export async function GET(req: NextRequest) {
  try {
    const db = await getDb();
    if (!db) {
      return NextResponse.json([]);
    }

    const limit = parseInt(req.nextUrl.searchParams.get("limit") || "20");

    const rows = await db
      .collection(COLLECTIONS.screenings)
      .find({}, {
        projection: {
          screening_id: 1,
          timestamp: 1,
          _riskLevel: 1,
          _riskScore: 1,
          _recommendation: 1,
          _passportNumber: 1,
          _holderName: 1,
          _tampered: 1,
          _faceMatch: 1,
        },
      })
      .sort({ _savedAt: -1 })
      .limit(limit)
      .toArray();

    return NextResponse.json(rows);
  } catch (err) {
    console.error("[VeriGate] Failed to fetch screenings:", err);
    return NextResponse.json([], { status: 500 });
  }
}
