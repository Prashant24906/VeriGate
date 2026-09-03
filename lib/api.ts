// In the browser: always use the Next.js rewrite proxy (/api/backend → FastAPI).
// This works both locally (next dev rewrites to localhost:8000) and on Vercel
// (next rewrites to NEXT_PUBLIC_API_URL which should be the deployed backend URL).
// In server components/actions use the direct URL so it works server-side too.
const API_BASE =
  typeof window === "undefined"
    ? process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
    : "/api/backend";

export interface ScreeningResult {
  screening_id: string;
  timestamp: string;
  document: Record<string, unknown>;
  validation: Record<string, unknown>;
  tampering: {
    tampered: boolean;
    confidence: number;
    tampering_score: number;
    risk_level: string;
    visualization_heatmap_b64?: string;
    details?: Record<string, unknown>;
  };
  face_verification: {
    face_detected: boolean;
    document_face_detected: boolean;
    verification_face_detected: boolean;
    similarity: number;
    match: boolean;
    confidence: number;
    document_face_b64?: string;
    verification_face_b64?: string;
    message?: string;
  };
  risk_assessment: {
    overall_risk_score: number;
    risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
    recommendation: string;
    breakdown: Record<string, number>;
    flags: string[];
  };
  disclaimer: string;
}

export interface ScreeningStats {
  total: number;
  low_risk: number;
  medium_risk: number;
  high_risk: number;
  critical_risk: number;
  pass_rate: number;
  tampered_count: number;
  face_mismatch_count: number;
}

export interface RecentScreening {
  screening_id: string;
  timestamp: string;
  document_type: string;
  passport_number?: string;
  holder_name?: string;
  nationality?: string;
  validation_status: string;
  tampering_status: string;
  face_match_status: string;
  risk_score: number;
  risk_level: string;
  recommendation: string;
  // MongoDB-flattened fields written by /api/screenings POST handler
  _holderName?: string;
  _passportNumber?: string;
  _riskScore?: number;
  _riskLevel?: string;
  _recommendation?: string;
  _tampered?: boolean;
  _faceMatch?: boolean;
}

export async function screenDocument(
  documentFile: File,
  verificationPhoto?: File,
  documentType = "passport"
): Promise<ScreeningResult> {
  const formData = new FormData();
  formData.append("document", documentFile);
  formData.append("document_type", documentType);
  if (verificationPhoto) {
    formData.append("verification_photo", verificationPhoto);
  }

  const response = await fetch(`${API_BASE}/screen`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || `Screening failed: ${response.status}`);
  }

  return response.json();
}

export async function getStats(): Promise<ScreeningStats> {
  const response = await fetch(`${API_BASE}/stats`);
  if (!response.ok) throw new Error("Failed to load stats");
  return response.json();
}

export async function getRecentScreenings(limit = 20): Promise<RecentScreening[]> {
  const response = await fetch(`${API_BASE}/recent?limit=${limit}`);
  if (!response.ok) throw new Error("Failed to load recent screenings");
  return response.json();
}

export async function getScreeningById(id: string): Promise<ScreeningResult> {
  const response = await fetch(`${API_BASE}/result/${id}`);
  if (!response.ok) throw new Error("Screening not found");
  return response.json();
}

export async function checkWatchlist(passportNumber: string) {
  const response = await fetch(
    `${API_BASE}/watchlist?passport_number=${encodeURIComponent(passportNumber)}`
  );
  if (!response.ok) throw new Error("Watchlist query failed");
  return response.json();
}

export async function healthCheck() {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) throw new Error("Backend unreachable");
  return response.json();
}
