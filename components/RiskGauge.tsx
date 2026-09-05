"use client";

import { motion } from "framer-motion";

interface RiskGaugeProps {
  score: number; // 0-100
  level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  recommendation: string;
}

const levelConfig = {
  LOW: { color: "#1F5C4A", label: "Low Risk", glow: "0 0 20px rgba(31,92,74,0.25)" },
  MEDIUM: { color: "#D98A1F", label: "Medium Risk", glow: "0 0 20px rgba(217,138,31,0.3)" },
  HIGH: { color: "#E85D42", label: "High Risk", glow: "0 0 20px rgba(232,93,66,0.3)" },
  CRITICAL: { color: "#C0392B", label: "Critical Risk", glow: "0 0 20px rgba(192,57,43,0.35)" },
};

export default function RiskGauge({ score, level, recommendation }: RiskGaugeProps) {
  // Defensive guard — backend may return undefined/null/NaN
  const safeScore = isNaN(score) || score == null ? 0 : Math.min(100, Math.max(0, score));
  const config = levelConfig[level] || levelConfig.HIGH;
  const radius = 80;
  const stroke = 10;
  const normalizedRadius = radius - stroke / 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const arcLength = circumference * 0.75;
  const offset = circumference * 0.25 / 2;
  const progressOffset = arcLength - (safeScore / 100) * arcLength;

  return (
    <div className="risk-gauge-wrapper">
      <div className="risk-gauge-svg-container" style={{ filter: config.glow }}>
        <svg height={radius * 2} width={radius * 2} style={{ transform: "rotate(135deg)" }}>
          {/* Track */}
          <circle
            stroke="rgba(23,31,51,0.1)"
            fill="transparent"
            strokeWidth={stroke}
            strokeDasharray={`${arcLength} ${circumference}`}
            strokeDashoffset={-offset}
            strokeLinecap="round"
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />
          {/* Progress */}
          <motion.circle
            stroke={config.color}
            fill="transparent"
            strokeWidth={stroke}
            strokeDasharray={`${arcLength} ${circumference}`}
            strokeLinecap="round"
            r={normalizedRadius}
            cx={radius}
            cy={radius}
            initial={{ strokeDashoffset: arcLength - offset }}
            animate={{ strokeDashoffset: progressOffset - offset }}
            transition={{ duration: 1.5, ease: "easeOut" }}
          />
        </svg>

        {/* Center Score */}
        <div className="risk-gauge-center">
          <motion.span
            className="risk-score-number"
            style={{ color: config.color }}
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5, duration: 0.5 }}
          >
            {safeScore}
          </motion.span>
          <span className="risk-score-label">/ 100</span>
        </div>
      </div>

      <motion.div
        className="risk-level-badge"
        style={{ background: `${config.color}22`, borderColor: `${config.color}55`, color: config.color }}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
      >
        {config.label}
      </motion.div>

      <motion.p
        className="risk-recommendation"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
      >
        {recommendation}
      </motion.p>
    </div>
  );
}
