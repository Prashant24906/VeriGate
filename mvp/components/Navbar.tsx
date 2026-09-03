"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Shield, ScanLine, LayoutDashboard, ListChecks, Menu, X } from "lucide-react";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const navLinks = [
  { href: "/", label: "Home", icon: Shield },
  { href: "/screen", label: "Screen", icon: ScanLine },
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/watchlist", label: "Watchlist", icon: ListChecks },
];

export default function Navbar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="navbar">
      <div className="navbar-inner">
        {/* Logo */}
        <Link href="/" className="navbar-logo">
          <div className="logo-icon">
            <Shield size={20} strokeWidth={2.5} />
          </div>
          <span className="logo-text">
            Veri<span className="logo-accent">Gate</span>
            <span className="logo-tag"> AI</span>
          </span>
        </Link>

        {/* Desktop Nav */}
        <nav className="navbar-links">
          {navLinks.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link key={href} href={href} className={`nav-link ${active ? "nav-link-active" : ""}`}>
                <Icon size={16} />
                {label}
                {active && (
                  <motion.div
                    className="nav-active-indicator"
                    layoutId="nav-indicator"
                    transition={{ type: "spring", stiffness: 380, damping: 30 }}
                  />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Status Badge */}
        <div className="navbar-status">
          <span className="status-dot" />
          <span className="status-text">System Online</span>
        </div>

        {/* Mobile Hamburger */}
        <button
          className="mobile-menu-btn"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle menu"
        >
          {mobileOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {/* Mobile Nav */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            className="mobile-nav"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            {navLinks.map(({ href, label, icon: Icon }) => {
              const active = pathname === href;
              return (
                <Link
                  key={href}
                  href={href}
                  className={`mobile-nav-link ${active ? "mobile-nav-link-active" : ""}`}
                  onClick={() => setMobileOpen(false)}
                >
                  <Icon size={18} />
                  {label}
                </Link>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
