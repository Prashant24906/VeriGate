"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { getScreeningById, type ScreeningResult } from "@/lib/api";
import ResultPanel from "@/components/ResultPanel";
import { ArrowLeft, Loader2 } from "lucide-react";
import Link from "next/link";
import { use } from "react";

export default function ResultPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [result, setResult] = useState<ScreeningResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getScreeningById(id)
      .then(setResult)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  return (
    <div className="screen-page">
      <div className="screen-page-header">
        <Link href="/dashboard">
          <button className="reset-btn" style={{ marginBottom: "1rem" }}>
            <ArrowLeft size={16} />
            Back to Dashboard
          </button>
        </Link>
        <h1 className="page-title">Screening Report</h1>
        <p className="page-subtitle">Full audit record for screening ID: <code>{id}</code></p>
      </div>

      {loading && (
        <div className="table-loading">
          <Loader2 size={24} className="spin" />
          Loading report...
        </div>
      )}

      {error && (
        <div className="dashboard-error">{error}</div>
      )}

      {result && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <ResultPanel result={result} />
        </motion.div>
      )}
    </div>
  );
}
