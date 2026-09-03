"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { useState } from "react";
import {
  Shield, ScanLine, Eye, Brain, UserCheck, Database,
  ArrowRight, Zap, Globe, CheckCircle2,
} from "lucide-react";

/* ─── Data ─────────────────────────────────────────────────────────── */
const features = [
  {
    icon: ScanLine,
    title: "Passport OCR & MRZ Parsing",
    desc: "Extracts identity fields with ICAO 9303 TD3 checksum validation — passport number, DOB, expiry, and composite checksum.",
    color: "#00d4ff",
  },
  {
    icon: Eye,
    title: "Image Forensics & Tampering",
    desc: "Error Level Analysis (ELA), Noise Variance, and Edge Discontinuity detection — with heatmap visualizations of anomalies.",
    color: "#a78bfa",
  },
  {
    icon: UserCheck,
    title: "1-to-1 Face Verification",
    desc: "Automated face crop extraction and similarity comparison between document photo and live selfie.",
    color: "#00ff88",
  },
  {
    icon: Brain,
    title: "Explainable Risk Scoring",
    desc: "Configurable weighted engine (Tampering 35%, Face 30%, Validity 20%, MRZ 10%, Blacklist 5%) with actionable recommendations.",
    color: "#ffd700",
  },
  {
    icon: Database,
    title: "MongoDB Audit Trail",
    desc: "Every screening is persisted with full metadata for compliance, review, and analytics via the integrated MongoDB store.",
    color: "#ff6b35",
  },
  {
    icon: Globe,
    title: "Multi-Document Ready",
    desc: "Extensible BaseDocumentProcessor interface for Passports, Visas, National IDs, and Residence Permits.",
    color: "#ff6bff",
  },
];

const steps = [
  { n: "01", title: "Upload Document", desc: "Upload a passport image to the system.", icon: ScanLine },
  { n: "02", title: "AI Pipeline Runs", desc: "OCR → MRZ → Validation → Tampering → Face → Risk.", icon: Zap },
  { n: "03", title: "Get Risk Report", desc: "Receive an explainable risk score with detailed findings.", icon: Shield },
];

const statsData = [
  { value: "99.2%", label: "MRZ Accuracy" },
  { value: "5", label: "AI Modules" },
  { value: "< 3s", label: "Avg Screen Time" },
  { value: "4", label: "Risk Levels" },
];

const verdicts = [
  { level: "LOW",      color: "#00ff88", action: "Proceed",             desc: "All checks passed. No anomalies detected." },
  { level: "MEDIUM",   color: "#ffd700", action: "Manual Review",       desc: "Minor issues found. Recommend secondary check." },
  { level: "HIGH",     color: "#ff6b35", action: "Secondary Inspection", desc: "Significant risk indicators. Halt and inspect." },
  { level: "CRITICAL", color: "#ff1744", action: "Detain for Review",   desc: "Multiple critical flags. Immediate intervention." },
];

const shieldRings = [
  { size: 230, duration: 8,  color: "rgba(0,212,255,0.2)",    dir: 1  },
  { size: 300, duration: 14, color: "rgba(167,139,250,0.15)", dir: -1 },
  { size: 380, duration: 20, color: "rgba(0,212,255,0.08)",   dir: 1  },
];

/* ─── Feature Card (needs hover state) ─────────────────────────────── */
function FeatureCard({ f, delay }: { f: typeof features[0]; delay: number }) {
  const [hovered, setHovered] = useState(false);
  return (
    <motion.div
      onHoverStart={() => setHovered(true)}
      onHoverEnd={() => setHovered(false)}
      whileHover={{ y: -4 }}
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      viewport={{ once: true }}
      style={{
        background: hovered ? "#0d1f2d" : "#0a1628",
        border: `1px solid ${hovered ? `${f.color}55` : "rgba(255,255,255,0.07)"}`,
        borderRadius: 16,
        padding: "1.75rem",
        transition: "border-color 0.3s, background 0.3s",
        position: "relative",
        overflow: "hidden",
        cursor: "default",
      }}
    >
      {/* Glow top border on hover */}
      {hovered && (
        <div style={{
          position: "absolute", top: 0, left: 0, right: 0, height: 1,
          background: `linear-gradient(90deg, transparent, ${f.color}, transparent)`,
        }} />
      )}
      <div style={{
        width: 48, height: 48, borderRadius: 12, marginBottom: "1rem",
        display: "flex", alignItems: "center", justifyContent: "center",
        background: `${f.color}18`, color: f.color,
      }}>
        <f.icon size={24} />
      </div>
      <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "#f1f5f9", marginBottom: "0.5rem" }}>
        {f.title}
      </h3>
      <p style={{ fontSize: "0.875rem", color: "#94a3b8", lineHeight: 1.65 }}>
        {f.desc}
      </p>
    </motion.div>
  );
}

/* ─── Page ──────────────────────────────────────────────────────────── */
export default function HomePage() {
  return (
    <div style={{ flex: 1 }}>

      {/* ── HERO ─────────────────────────────────────────────────── */}
      <section style={{
        position: "relative",
        overflow: "hidden",
        minHeight: "calc(100vh - 64px)",
        display: "flex",
        alignItems: "stretch",
        width: "100%",
        background: "linear-gradient(135deg, #020b18 0%, #030d1a 50%, #040f1e 100%)",
      }}>
        {/* Grid pattern */}
        <div style={{
          position: "fixed", inset: 0, pointerEvents: "none", zIndex: 0,
          backgroundImage:
            "linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px)," +
            "linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px)",
          backgroundSize: "50px 50px",
        }} />

        {/* Glow blobs */}
        <div style={{
          position: "absolute", borderRadius: "50%", filter: "blur(80px)",
          pointerEvents: "none", width: 700, height: 700,
          background: "radial-gradient(circle, rgba(0,212,255,0.1) 0%, transparent 70%)",
          top: -200, left: -150,
        }} />
        <div style={{
          position: "absolute", borderRadius: "50%", filter: "blur(80px)",
          pointerEvents: "none", width: 600, height: 600,
          background: "radial-gradient(circle, rgba(100,50,255,0.1) 0%, transparent 70%)",
          bottom: -150, right: 50,
        }} />

        {/* Inner flex row */}
        <div style={{
          display: "flex", alignItems: "center", justifyContent: "space-between",
          gap: "4rem", maxWidth: 1400, margin: "0 auto",
          padding: "3rem 2rem", width: "100%", flex: 1, position: "relative", zIndex: 1,
        }}>

          {/* ── Left: Text content ── */}
          <motion.div
            style={{ flex: 1, maxWidth: 620, minWidth: 0 }}
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
          >
            {/* Badge */}
            <motion.div
              style={{
                display: "inline-flex", alignItems: "center", gap: 7,
                background: "rgba(0,212,255,0.08)",
                border: "1px solid rgba(0,212,255,0.3)",
                color: "#00d4ff", fontSize: "0.8rem", fontWeight: 600,
                padding: "5px 14px", borderRadius: 20, marginBottom: "1.5rem",
                letterSpacing: "0.02em",
              }}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
            >
              <Shield size={14} />
              SIH 2026 · Intelligent Border Security
            </motion.div>

            {/* Heading */}
            <h1 style={{
              fontSize: "clamp(2.4rem, 4vw, 4rem)", fontWeight: 900,
              lineHeight: 1.1, marginBottom: "1.5rem",
              display: "flex", flexDirection: "column", letterSpacing: "-0.02em",
            }}>
              <span style={{ color: "#f1f5f9" }}>AI-Powered</span>
              <span style={{
                background: "linear-gradient(90deg, #00d4ff, #0090ff, #a78bfa)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                backgroundClip: "text",
              }}>
                Document Verification
              </span>
              <span style={{ color: "#f1f5f9" }}>at the Border</span>
            </h1>

            {/* Subtitle */}
            <p style={{
              color: "#94a3b8", fontSize: "1.1rem", lineHeight: 1.8,
              marginBottom: "2.5rem", maxWidth: 540,
            }}>
              VeriGate AI is a modular, multi-layer identity screening platform using OCR,
              image forensics, facial verification, and explainable risk scoring — built for
              border security, passport control, and fraud detection.
            </p>

            {/* CTAs */}
            <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
              <Link href="/screen">
                <motion.div
                  style={{
                    display: "inline-flex", alignItems: "center", gap: 8,
                    background: "linear-gradient(135deg, #00d4ff, #0070ff)",
                    color: "#fff", fontWeight: 700, fontSize: "0.95rem",
                    padding: "12px 24px", borderRadius: 12, cursor: "pointer",
                    boxShadow: "0 4px 30px rgba(0,212,255,0.3)",
                  }}
                  whileHover={{ scale: 1.04, boxShadow: "0 6px 40px rgba(0,212,255,0.5)" }}
                  whileTap={{ scale: 0.97 }}
                >
                  <ScanLine size={20} />
                  Start Screening
                  <ArrowRight size={18} />
                </motion.div>
              </Link>
              <Link href="/dashboard">
                <motion.div
                  style={{
                    display: "inline-flex", alignItems: "center", gap: 8,
                    background: "transparent", color: "#f1f5f9", fontWeight: 600,
                    fontSize: "0.95rem", padding: "12px 24px", borderRadius: 12,
                    cursor: "pointer", border: "1px solid rgba(255,255,255,0.15)",
                  }}
                  whileHover={{ scale: 1.04, backgroundColor: "rgba(0,212,255,0.08)" }}
                  whileTap={{ scale: 0.97 }}
                >
                  View Dashboard
                </motion.div>
              </Link>
            </div>
          </motion.div>

          {/* ── Right: Animated Shield ── */}
          <motion.div
            style={{
              position: "relative", width: 380, height: 380,
              display: "flex", alignItems: "center", justifyContent: "center",
              flexShrink: 0, zIndex: 1,
            }}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4, duration: 0.8 }}
          >
            {/* Spinning rings via framer-motion */}
            {shieldRings.map((ring, i) => (
              <motion.div
                key={i}
                style={{
                  position: "absolute",
                  width: ring.size, height: ring.size,
                  borderRadius: "50%",
                  border: `1px solid ${ring.color}`,
                }}
                animate={{ rotate: ring.dir === 1 ? 360 : -360 }}
                transition={{ duration: ring.duration, repeat: Infinity, ease: "linear" }}
              />
            ))}

            {/* Core */}
            <div style={{
              width: 130, height: 130,
              background: "linear-gradient(135deg, rgba(0,212,255,0.15), rgba(0,112,255,0.1))",
              border: "1px solid rgba(0,212,255,0.4)", borderRadius: 32,
              display: "flex", alignItems: "center", justifyContent: "center",
              color: "#00d4ff",
              boxShadow: "0 0 80px rgba(0,212,255,0.25), inset 0 0 40px rgba(0,212,255,0.05)",
              zIndex: 1,
            }}>
              <Shield size={80} strokeWidth={1.5} />
            </div>

            {/* Orbit dots */}
            {[0, 60, 120, 180, 240, 300].map((deg, i) => (
              <motion.div
                key={deg}
                style={{
                  position: "absolute", width: 8, height: 8, borderRadius: "50%",
                  background: "#00d4ff", boxShadow: "0 0 10px #00d4ff",
                  transform: `rotate(${deg}deg) translateX(145px) rotate(-${deg}deg)`,
                }}
                animate={{ opacity: [0.4, 1, 0.4] }}
                transition={{ duration: 2, delay: i * 0.3, repeat: Infinity }}
              />
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── STATS STRIP ──────────────────────────────────────────── */}
      <section style={{
        display: "flex", justifyContent: "center",
        borderTop: "1px solid rgba(255,255,255,0.07)",
        borderBottom: "1px solid rgba(255,255,255,0.07)",
        background: "#0a1628",
      }}>
        {statsData.map((s, i) => (
          <motion.div
            key={s.label}
            style={{
              flex: 1, display: "flex", flexDirection: "column",
              alignItems: "center", padding: "1.75rem 1rem", gap: 4,
              borderRight: i < statsData.length - 1 ? "1px solid rgba(255,255,255,0.07)" : "none",
            }}
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            viewport={{ once: true }}
          >
            <span style={{
              fontSize: "1.75rem", fontWeight: 800,
              background: "linear-gradient(90deg, #00d4ff, #a78bfa)",
              WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text",
            }}>{s.value}</span>
            <span style={{
              fontSize: "0.8rem", color: "#64748b",
              textTransform: "uppercase", letterSpacing: "0.08em",
            }}>{s.label}</span>
          </motion.div>
        ))}
      </section>

      {/* ── AI MODULE SUITE ──────────────────────────────────────── */}
      <section style={{ padding: "5rem 2rem", maxWidth: 1400, margin: "0 auto", width: "100%" }}>
        <motion.div
          style={{ textAlign: "center", marginBottom: "3rem" }}
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          <h2 style={{ fontSize: "clamp(1.6rem, 3vw, 2.2rem)", fontWeight: 800, color: "#f1f5f9", marginBottom: "0.75rem" }}>
            AI Module Suite
          </h2>
          <p style={{ color: "#94a3b8", fontSize: "1rem", maxWidth: 500, margin: "0 auto" }}>
            Six independent, composable AI modules running as a single pipeline.
          </p>
        </motion.div>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
          gap: "1.25rem",
        }}>
          {features.map((f, i) => (
            <FeatureCard key={f.title} f={f} delay={i * 0.1} />
          ))}
        </div>
      </section>

      {/* ── HOW IT WORKS ─────────────────────────────────────────── */}
      <section style={{ padding: "5rem 2rem", background: "#0a1628", width: "100%" }}>
        <motion.div
          style={{ textAlign: "center", marginBottom: "3rem", maxWidth: 1400, margin: "0 auto 3rem" }}
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          <h2 style={{ fontSize: "clamp(1.6rem, 3vw, 2.2rem)", fontWeight: 800, color: "#f1f5f9", marginBottom: "0.75rem" }}>
            How It Works
          </h2>
          <p style={{ color: "#94a3b8", fontSize: "1rem" }}>
            A 3-step process from document upload to risk verdict.
          </p>
        </motion.div>

        <div style={{
          display: "flex", gap: "2rem", justifyContent: "center",
          flexWrap: "wrap", maxWidth: 1400, margin: "0 auto",
        }}>
          {steps.map((step, i) => (
            <motion.div
              key={step.n}
              style={{
                flex: 1, minWidth: 220, maxWidth: 300,
                background: "#0d1f2d", border: "1px solid rgba(255,255,255,0.07)",
                borderRadius: 16, padding: "2rem 1.5rem", textAlign: "center",
              }}
              initial={{ opacity: 0, x: i % 2 === 0 ? -20 : 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.15 }}
              viewport={{ once: true }}
            >
              <span style={{
                fontFamily: "monospace", fontSize: "0.75rem", fontWeight: 500,
                color: "#00d4ff", letterSpacing: "0.1em",
                background: "rgba(0,212,255,0.08)", border: "1px solid rgba(0,212,255,0.2)",
                padding: "2px 8px", borderRadius: 20, display: "inline-block", marginBottom: "1.25rem",
              }}>{step.n}</span>
              <div style={{
                width: 60, height: 60, borderRadius: 16, margin: "0 auto 1rem",
                background: "rgba(0,212,255,0.08)", border: "1px solid rgba(0,212,255,0.2)",
                display: "flex", alignItems: "center", justifyContent: "center", color: "#00d4ff",
              }}>
                <step.icon size={26} />
              </div>
              <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "#f1f5f9", marginBottom: "0.5rem" }}>
                {step.title}
              </h3>
              <p style={{ fontSize: "0.85rem", color: "#94a3b8" }}>{step.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── RISK VERDICTS ────────────────────────────────────────── */}
      <section style={{ padding: "5rem 2rem", maxWidth: 1400, margin: "0 auto", width: "100%" }}>
        <motion.div
          style={{ textAlign: "center", marginBottom: "3rem" }}
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          <h2 style={{ fontSize: "clamp(1.6rem, 3vw, 2.2rem)", fontWeight: 800, color: "#f1f5f9", marginBottom: "0.75rem" }}>
            Risk Verdicts
          </h2>
        </motion.div>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          gap: "1.25rem",
        }}>
          {verdicts.map((v, i) => (
            <motion.div
              key={v.level}
              style={{
                background: "#0a1628", border: `1px solid ${v.color}44`,
                borderRadius: 16, padding: "1.75rem 1.25rem", textAlign: "center",
                display: "flex", flexDirection: "column", alignItems: "center", gap: "0.5rem",
              }}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.1 }}
              viewport={{ once: true }}
            >
              <div style={{ fontFamily: "monospace", fontSize: "0.75rem", fontWeight: 700, letterSpacing: "0.1em", color: v.color }}>
                {v.level}
              </div>
              <CheckCircle2 size={20} style={{ color: v.color }} />
              <div style={{ fontSize: "1rem", fontWeight: 700, color: v.color }}>{v.action}</div>
              <p style={{ fontSize: "0.8rem", color: "#94a3b8", marginTop: "0.25rem" }}>{v.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── CTA BANNER ───────────────────────────────────────────── */}
      <section style={{
        background: "linear-gradient(135deg, rgba(0,212,255,0.07), rgba(0,70,255,0.07))",
        borderTop: "1px solid rgba(255,255,255,0.07)",
        borderBottom: "1px solid rgba(255,255,255,0.07)",
        padding: "4rem 2rem",
      }}>
        <motion.div
          style={{ maxWidth: 1400, margin: "0 auto", textAlign: "center" }}
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <h2 style={{ fontSize: "clamp(1.5rem, 3vw, 2rem)", fontWeight: 800, color: "#f1f5f9", marginBottom: "0.75rem" }}>
            Ready to Screen a Document?
          </h2>
          <p style={{ color: "#94a3b8", marginBottom: "2rem", fontSize: "1rem" }}>
            Upload a passport image and run the full AI pipeline in seconds.
          </p>
          <Link href="/screen">
            <motion.div
              style={{
                display: "inline-flex", alignItems: "center", gap: 8, margin: "0 auto",
                background: "linear-gradient(135deg, #00d4ff, #0070ff)",
                color: "#fff", fontWeight: 700, fontSize: "0.95rem",
                padding: "12px 28px", borderRadius: 12, cursor: "pointer",
                boxShadow: "0 4px 30px rgba(0,212,255,0.3)",
              }}
              whileHover={{ scale: 1.04, boxShadow: "0 6px 40px rgba(0,212,255,0.5)" }}
              whileTap={{ scale: 0.97 }}
            >
              <ScanLine size={20} />
              Start Screening Now
              <ArrowRight size={18} />
            </motion.div>
          </Link>
        </motion.div>
      </section>

    </div>
  );
}
