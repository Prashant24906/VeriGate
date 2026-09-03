import { NextResponse } from "next/server";
import { getDb, COLLECTIONS } from "@/lib/mongodb";

// GET /api/stats — aggregate dashboard statistics from MongoDB
export async function GET() {
  try {
    const db = await getDb();

    if (!db) {
      return NextResponse.json({
        total: 0,
        low_risk: 0,
        medium_risk: 0,
        high_risk: 0,
        critical_risk: 0,
        pass_rate: 0,
        tampered_count: 0,
        face_mismatch_count: 0,
      });
    }

    const col = db.collection(COLLECTIONS.screenings);

    const [total, low, medium, high, critical, tampered, faceMismatch] = await Promise.all([
      col.countDocuments(),
      col.countDocuments({ _riskLevel: "LOW" }),
      col.countDocuments({ _riskLevel: "MEDIUM" }),
      col.countDocuments({ _riskLevel: "HIGH" }),
      col.countDocuments({ _riskLevel: "CRITICAL" }),
      col.countDocuments({ _tampered: true }),
      col.countDocuments({ _faceMatch: false }),
    ]);

    return NextResponse.json({
      total,
      low_risk: low,
      medium_risk: medium,
      high_risk: high,
      critical_risk: critical,
      pass_rate: total > 0 ? +(low / total).toFixed(3) : 0,
      tampered_count: tampered,
      face_mismatch_count: faceMismatch,
    });
  } catch (err) {
    console.error("[VeriGate] Failed to compute stats:", err);
    return NextResponse.json({ error: String(err) }, { status: 500 });
  }
}
