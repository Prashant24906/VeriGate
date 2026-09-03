import { Shield, GitBranch } from "lucide-react";
import Link from "next/link";

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <div className="footer-logo">
            <Shield size={18} strokeWidth={2.5} />
            <span>
              Veri<span className="logo-accent">Gate</span> AI
            </span>
          </div>
          <p className="footer-tagline">
            Intelligent Document &amp; Identity Verification
          </p>
        </div>

        <nav className="footer-links">
          <Link href="/" className="footer-link">Home</Link>
          <Link href="/screen" className="footer-link">Screen</Link>
          <Link href="/dashboard" className="footer-link">Dashboard</Link>
          <Link href="/watchlist" className="footer-link">Watchlist</Link>
        </nav>

        <div className="footer-meta">
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="footer-github"
          >
            <GitBranch size={16} />
            GitHub
          </a>
          <span className="footer-sih">SIH Prototype 2026</span>
        </div>
      </div>

      <div className="footer-disclaimer">
        ⚠️ VeriGate AI is an AI-assisted screening prototype intended to support human decision-making.
        It does not replace authorized border, immigration, law-enforcement, or government decision-making.
        All sample documents are synthetic demo data.
      </div>
    </footer>
  );
}
