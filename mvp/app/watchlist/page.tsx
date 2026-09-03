"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { checkWatchlist } from "@/lib/api";
import { ListChecks, Search, ShieldAlert, ShieldCheck, Loader2 } from "lucide-react";

export default function WatchlistPage() {
  const [passportNumber, setPassportNumber] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<null | { found: boolean; details?: unknown; message?: string; disclaimer?: string }>(null);
  const [error, setError] = useState("");

  const handleSearch = async () => {
    if (!passportNumber.trim()) return;
    setLoading(true);
    setResult(null);
    setError("");
    try {
      const res = await checkWatchlist(passportNumber.trim());
      setResult(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Search failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="watchlist-page">
      <div className="watchlist-header">
        <h1 className="page-title">
          <ListChecks size={28} />
          Watchlist Checker
        </h1>
        <p className="page-subtitle">
          Search the demo synthetic watchlist database by passport number.
        </p>
      </div>

      <motion.div
        className="watchlist-search-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="search-input-row">
          <div className="search-input-wrapper">
            <Search size={18} className="search-icon" />
            <input
              id="passport-number-input"
              type="text"
              className="search-input"
              placeholder="Enter Passport Number (e.g. X9988776)"
              value={passportNumber}
              onChange={(e) => setPassportNumber(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            />
          </div>
          <motion.button
            className="search-btn"
            onClick={handleSearch}
            disabled={loading || !passportNumber.trim()}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {loading ? <Loader2 size={18} className="spin" /> : <Search size={18} />}
            Search
          </motion.button>
        </div>

        <div className="watchlist-example-chips">
          {["X9988776", "AB1234567", "ZZ9999999"].map((p) => (
            <button
              key={p}
              className="example-chip"
              onClick={() => setPassportNumber(p)}
            >
              {p}
            </button>
          ))}
        </div>
      </motion.div>

      {error && (
        <div className="watchlist-error">
          {error}
        </div>
      )}

      <AnimatePresence>
        {result && (
          <motion.div
            className={`watchlist-result-card ${result.found ? "watchlist-hit" : "watchlist-clear"}`}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            {result.found ? (
              <>
                <ShieldAlert size={40} className="text-red-400" />
                <h2 className="watchlist-result-title text-red-400">⚠ Watchlist Hit</h2>
                <p className="watchlist-result-msg">
                  Passport number <code>{passportNumber}</code> has been flagged in the demo watchlist.
                </p>
                {result.details && (
                  <pre className="watchlist-details">
                    {JSON.stringify(result.details, null, 2)}
                  </pre>
                )}
                {result.disclaimer && (
                  <p className="watchlist-disclaimer">{result.disclaimer}</p>
                )}
              </>
            ) : (
              <>
                <ShieldCheck size={40} className="text-green-400" />
                <h2 className="watchlist-result-title text-green-400">✓ No Match Found</h2>
                <p className="watchlist-result-msg">
                  Passport number <code>{passportNumber}</code> is not in the demo watchlist.
                </p>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      <div className="watchlist-demo-note">
        <p>💡 <strong>Demo Note:</strong> This watchlist contains synthetic data generated for SIH evaluation purposes only. Try <code>X9988776</code> for a watchlist hit demo.</p>
      </div>
    </div>
  );
}
