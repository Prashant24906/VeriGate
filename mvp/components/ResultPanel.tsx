"use client";

import { motion } from "framer-motion";
import RiskGauge from "./RiskGauge";
import type { ScreeningResult } from "@/lib/api";
import {
  CheckCircle, XCircle, AlertTriangle, User, FileText,
  ShieldCheck, ShieldAlert, Eye, BarChart2, Clock
} from "lucide-react";

interface ResultPanelProps {
  result: ScreeningResult;
}

function StatusIcon({ ok }: { ok: boolean }) {
  return ok
    ? <CheckCircle size={16} className="text-green-400" />
    : <XCircle size={16} className="text-red-400" />;
}

function SectionCard({
  title, icon: Icon, children, delay = 0
}: {
  title: string;
  icon: React.ElementType;
  children: React.ReactNode;
  delay?: number;
}) {
  return (
    <motion.div
      className="result-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
    >
      <div className="result-card-header">
        <Icon size={18} className="result-card-icon" />
        <h3 className="result-card-title">{title}</h3>
      </div>
      <div className="result-card-body">{children}</div>
    </motion.div>
  );
}

function Field({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="result-field">
      <span className="result-field-label">{label}</span>
      <span className="result-field-value">{String(value ?? "—")}</span>
    </div>
  );
}

export default function ResultPanel({ result }: ResultPanelProps) {
  const { document: doc, validation, tampering, face_verification: face, risk_assessment: risk } = result;

  const docFields = doc as Record<string, unknown>;
  const valFields = validation as Record<string, unknown>;

  return (
    <div className="result-panel">
      {/* Screening ID */}
      <motion.div
        className="screening-id-bar"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <Clock size={14} />
        <span>Screening ID: <code>{result.screening_id}</code></span>
        <span className="screening-ts">{new Date(result.timestamp).toLocaleString()}</span>
      </motion.div>

      {/* Risk Gauge — Top Center */}
      <motion.div
        className="risk-gauge-section"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <RiskGauge
          score={Math.round(risk.overall_risk_score ?? risk.score ?? 0)}
          level={risk.risk_level ?? "LOW"}
          recommendation={risk.recommendation ?? "Proceed"}
        />
      </motion.div>

      {/* Risk Flags */}
      {risk.flags && risk.flags.length > 0 && (
        <motion.div
          className="risk-flags"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          {risk.flags.map((flag, i) => (
            <span key={i} className="risk-flag-chip">
              <AlertTriangle size={12} />
              {flag}
            </span>
          ))}
        </motion.div>
      )}

      {/* Risk Breakdown */}
      {risk.breakdown && (
        <SectionCard title="Risk Breakdown" icon={BarChart2} delay={0.3}>
          <div className="risk-breakdown-grid">
            {Object.entries(risk.breakdown).map(([key, val]) => (
              <div key={key} className="risk-breakdown-item">
                <div className="risk-breakdown-label">{key.replace(/_/g, " ")}</div>
                <div className="risk-breakdown-bar-track">
                  <motion.div
                    className="risk-breakdown-bar"
                    style={{ background: val > 60 ? "#ff6b35" : val > 30 ? "#ffd700" : "#00ff88" }}
                    initial={{ width: 0 }}
                    animate={{ width: `${val}%` }}
                    transition={{ delay: 0.6, duration: 0.8 }}
                  />
                </div>
                <span className="risk-breakdown-score">{Math.round(val)}</span>
              </div>
            ))}
          </div>
        </SectionCard>
      )}

      {/* Document Details */}
      <SectionCard title="Document Details" icon={FileText} delay={0.4}>
        <div className="fields-grid">
          <Field label="Document Type" value={docFields.document_type} />
          <Field label="Full Name" value={docFields.name || docFields.full_name} />
          <Field label="Passport No." value={docFields.passport_number} />
          <Field label="Date of Birth" value={docFields.date_of_birth} />
          <Field label="Nationality" value={docFields.nationality} />
          <Field label="Expiry Date" value={docFields.expiry_date} />
          <Field label="Issuing Country" value={docFields.issuing_country} />
          <Field label="OCR Confidence" value={docFields.confidence ? `${((docFields.confidence as number) * 100).toFixed(1)}%` : undefined} />
        </div>
      </SectionCard>

      {/* Validation */}
      <SectionCard title="Validation Checks" icon={ShieldCheck} delay={0.5}>
        <div className="validation-grid">
          {Object.entries(valFields).map(([key, val]) => {
            if (key === "watchlist_hit" || key === "errors" || key === "warnings") return null;
            if (typeof val === "boolean") {
              return (
                <div key={key} className="validation-item">
                  <StatusIcon ok={val} />
                  <span>{key.replace(/_/g, " ")}</span>
                </div>
              );
            }
            return null;
          })}
        </div>
        {Boolean(valFields.errors) && Array.isArray(valFields.errors) && (valFields.errors as string[]).length > 0 && (
          <div className="validation-errors">
            {(valFields.errors as string[]).map((e, i) => (
              <div key={i} className="validation-error-item">
                <XCircle size={14} /> {e}
              </div>
            ))}
          </div>
        )}
        {Boolean(valFields.watchlist_hit) && (
          <div className="watchlist-alert">
            <ShieldAlert size={16} />
            WATCHLIST HIT — Manual intervention required
          </div>
        )}
      </SectionCard>

      {/* Tampering */}
      <SectionCard title="Image Forensics" icon={Eye} delay={0.6}>
        <div className="tampering-summary">
          <StatusIcon ok={!tampering.tampered} />
          <span className={tampering.tampered ? "text-red-400 font-semibold" : "text-green-400 font-semibold"}>
            {tampering.tampered ? "Tampering Detected" : "No Tampering Detected"}
          </span>
          <span className="ml-auto tampering-score">
            Score: {Math.round(tampering.tampering_score * 100)}
          </span>
        </div>
        {tampering.visualization_heatmap_b64 && (
          <div className="heatmap-container">
            <p className="heatmap-label">ELA Heatmap</p>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={`data:image/png;base64,${tampering.visualization_heatmap_b64}`}
              alt="Tampering heatmap"
              className="heatmap-image"
            />
          </div>
        )}
      </SectionCard>

      {/* Face Verification */}
      <SectionCard title="Face Verification" icon={User} delay={0.7}>
        {!face.face_detected ? (
          <p className="face-no-upload">{face.message || "No verification photo provided."}</p>
        ) : (
          <>
            <div className="face-result-row">
              <StatusIcon ok={face.match} />
              <span className={face.match ? "text-green-400 font-semibold" : "text-red-400 font-semibold"}>
                {face.match ? "Face Match ✓" : "Face Mismatch ✗"}
              </span>
              <span className="face-similarity">
                Similarity: {(face.similarity * 100).toFixed(1)}%
              </span>
            </div>
            <div className="face-images">
              {face.document_face_b64 && (
                <div className="face-image-box">
                  <span>Document Photo</span>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={`data:image/png;base64,${face.document_face_b64}`} alt="Document face" />
                </div>
              )}
              {face.verification_face_b64 && (
                <div className="face-image-box">
                  <span>Verification Photo</span>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={`data:image/png;base64,${face.verification_face_b64}`} alt="Verification face" />
                </div>
              )}
            </div>
          </>
        )}
      </SectionCard>
    </div>
  );
}
