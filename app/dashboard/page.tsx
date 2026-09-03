"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { getStats, getRecentScreenings, type ScreeningStats, type RecentScreening } from "@/lib/api";
import { LayoutDashboard, TrendingUp, AlertTriangle, ShieldCheck, RefreshCw, ExternalLink } from "lucide-react";
import Link from "next/link";

const riskColors: Record<string, string> = {
  LOW: "#00ff88",
  MEDIUM: "#ffd700",
  HIGH: "#ff6b35",
  CRITICAL: "#ff1744",
};

function StatCard({ label, value, icon: Icon, color, delay }: {
  label: string;
  value: string | number;
  icon: React.ElementType;
  color: string;
  delay: number;
}) {
  return (
    <motion.div
      className="stat-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      style={{ borderColor: `${color}33` }}
    >
      <div className="stat-icon" style={{ background: `${color}18`, color }}>
        <Icon size={22} />
      </div>
      <div className="stat-info">
        <span className="stat-value" style={{ color }}>{value}</span>
        <span className="stat-label">{label}</span>
      </div>
    </motion.div>
  );
}

export default function DashboardPage() {
  const [stats, setStats] = useState<ScreeningStats | null>(null);
  const [recent, setRecent] = useState<RecentScreening[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const [statsRes, recentRes] = await Promise.all([
        fetch("/api/stats").then((r) => r.json()),
        fetch("/api/screenings?limit=20").then((r) => r.json()),
      ]);
      setStats(statsRes);
      setRecent(Array.isArray(recentRes) ? recentRes : []);
    } catch {
      setError("Failed to load dashboard data. Ensure MongoDB is configured in .env.local.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h1 className="page-title">
          <LayoutDashboard size={28} />
          Audit Dashboard
        </h1>
        <button className="refresh-btn" onClick={load} disabled={loading}>
          <RefreshCw size={16} className={loading ? "spin" : ""} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="dashboard-error">
          <AlertTriangle size={18} />
          {error}
        </div>
      )}

      {/* Stats Grid */}
      {stats && (
        <div className="stats-grid">
          <StatCard
            label="Total Screenings"
            value={stats.total ?? 0}
            icon={ShieldCheck}
            color="#00d4ff"
            delay={0}
          />
          <StatCard
            label="High Risk Detected"
            value={stats.high_risk ?? 0}
            icon={AlertTriangle}
            color="#ff6b35"
            delay={0.1}
          />
          <StatCard
            label="Pass Rate"
            value={`${((stats.pass_rate ?? 0) * 100).toFixed(1)}%`}
            icon={TrendingUp}
            color="#00ff88"
            delay={0.2}
          />
          <StatCard
            label="Tampered Docs"
            value={stats.tampered_count ?? 0}
            icon={ShieldCheck}
            color="#a78bfa"
            delay={0.3}
          />
        </div>
      )}

      {/* Recent Screenings Table */}
      <motion.div
        className="recent-table-card"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <div className="table-header">
          <h2 className="table-title">Recent Screenings</h2>
          <span className="table-count">{recent.length} records</span>
        </div>

        {loading ? (
          <div className="table-loading">
            <RefreshCw size={24} className="spin" />
            Loading...
          </div>
        ) : recent.length === 0 ? (
          <div className="table-empty">
            No screenings found. Run a screening to see results here.
          </div>
        ) : (
          <div className="table-wrapper">
            <table className="screenings-table">
              <thead>
                <tr>
                  <th>Screening ID</th>
                  <th>Timestamp</th>
                  <th>Name</th>
                  <th>Passport No.</th>
                  <th>Risk Level</th>
                  <th>Score</th>
                  <th>Recommendation</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {recent.map((s, i) => (
                  <motion.tr
                    key={s.screening_id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.05 * i }}
                    className="table-row"
                  >
                    <td className="id-cell">
                      <code>{s.screening_id.slice(0, 8)}…</code>
                    </td>
                    <td className="ts-cell">
                      {new Date(s.timestamp).toLocaleString()}
                    </td>
                    <td>{s._holderName || s.holder_name || "—"}</td>
                    <td><code>{s._passportNumber || s.passport_number || "—"}</code></td>
                    <td>
                      <span
                        className="risk-badge"
                        style={{
                          background: `${riskColors[s.risk_level] || "#fff"}22`,
                          color: riskColors[s.risk_level] || "#fff",
                          borderColor: `${riskColors[s.risk_level] || "#fff"}55`,
                        }}
                      >
                        {s.risk_level}
                      </span>
                    </td>
                    <td style={{ color: riskColors[s.risk_level] }}>
                      {Math.round(s._riskScore ?? s.risk_score ?? 0)}
                    </td>
                    <td className="rec-cell">{s.recommendation}</td>
                    <td>
                      <Link href={`/result/${s.screening_id}`} className="view-btn">
                        <ExternalLink size={14} />
                      </Link>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </motion.div>
    </div>
  );
}
