import type { Metadata } from "next";
import { Poppins } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800", "900"],
  variable: "--font-poppins",
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
    <html lang="en" className={poppins.variable}>
      <body>
        <Navbar />
        <main className="page-wrapper">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
