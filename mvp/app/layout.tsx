import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "VeriGate AI — Intelligent Document & Identity Verification",
  description:
    "AI-powered border security and passport verification platform featuring OCR, MRZ parsing, image forensics, facial verification, and explainable risk scoring. Built for SIH 2026.",
  keywords: ["border security", "passport verification", "OCR", "MRZ", "AI", "document fraud detection"],
  openGraph: {
    title: "VeriGate AI",
    description: "Intelligent Document & Identity Verification Platform",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body>
        <Navbar />
        <main className="page-wrapper">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
