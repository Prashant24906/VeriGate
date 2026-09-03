"use client";

import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { screenDocument, type ScreeningResult } from "@/lib/api";
import ResultPanel from "@/components/ResultPanel";
import {
  Upload, Camera, ScanLine, Loader2, AlertCircle,
  FileImage, X, CheckCircle2
} from "lucide-react";

type Step = "upload" | "scanning" | "results" | "error";

function DropZone({
  label,
  file,
  onFile,
  icon: Icon,
  accept = "image/*",
  id,
}: {
  label: string;
  file: File | null;
  onFile: (f: File) => void;
  icon: React.ElementType;
  accept?: string;
  id: string;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) onFile(f);
  };

  return (
    <div
      className={`dropzone ${dragging ? "dropzone-dragging" : ""} ${file ? "dropzone-filled" : ""}`}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
    >
      <input
        id={id}
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={(e) => { const f = e.target.files?.[0]; if (f) onFile(f); }}
      />
      {file ? (
        <div className="dropzone-preview">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={URL.createObjectURL(file)}
            alt="Preview"
            className="dropzone-img-preview"
          />
          <div className="dropzone-filename">
            <CheckCircle2 size={16} className="text-green-400" />
            <span>{file.name}</span>
          </div>
        </div>
      ) : (
        <div className="dropzone-placeholder">
          <Icon size={36} className="dropzone-icon" />
          <p className="dropzone-label">{label}</p>
          <p className="dropzone-hint">Click or drag & drop</p>
        </div>
      )}
    </div>
  );
}

export default function ScreenPage() {
  const [docFile, setDocFile] = useState<File | null>(null);
  const [faceFile, setFaceFile] = useState<File | null>(null);
  const [step, setStep] = useState<Step>("upload");
  const [result, setResult] = useState<ScreeningResult | null>(null);
  const [error, setError] = useState<string>("");
  const [scanProgress, setScanProgress] = useState(0);

  const handleScreen = async () => {
    if (!docFile) return;
    setStep("scanning");
    setScanProgress(0);

    // Fake progress animation
    const interval = setInterval(() => {
      setScanProgress((p) => {
        if (p >= 90) { clearInterval(interval); return 90; }
        return p + Math.random() * 15;
      });
    }, 400);

    try {
      const res = await screenDocument(docFile, faceFile ?? undefined);
      clearInterval(interval);
      setScanProgress(100);

      // Silently save to MongoDB (fire-and-forget — doesn't block UI)
      fetch("/api/screenings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(res),
      }).catch(() => {/* MongoDB not configured — that's OK */});

      await new Promise((r) => setTimeout(r, 500));
      setResult(res);
      setStep("results");
    } catch (err: unknown) {
      clearInterval(interval);
      setError(err instanceof Error ? err.message : "Unknown error");
      setStep("error");
    }
  };

  const reset = () => {
    setDocFile(null);
    setFaceFile(null);
    setStep("upload");
    setResult(null);
    setError("");
    setScanProgress(0);
  };

  const scanSteps = [
    "Extracting passport fields via OCR...",
    "Parsing MRZ checksums (ICAO 9303)...",
    "Running ELA image forensics...",
    "Analysing face similarity...",
    "Computing risk score...",
  ];
  const stepIndex = Math.floor((scanProgress / 100) * scanSteps.length);

  return (
    <div className="screen-page">
      <div className="screen-page-header">
        <h1 className="page-title">
          <ScanLine size={28} />
          Live AI Screening
        </h1>
        <p className="page-subtitle">
          Upload a passport document and an optional verification photo to run the full AI pipeline.
        </p>
      </div>

      <AnimatePresence mode="wait">
        {/* UPLOAD STEP */}
        {step === "upload" && (
          <motion.div
            key="upload"
            className="upload-section"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <div className="upload-grid">
              <div className="upload-col">
                <div className="upload-col-header">
                  <FileImage size={18} />
                  <span>Passport Document <span className="required-badge">Required</span></span>
                </div>
                <DropZone
                  id="passport-upload"
                  label="Upload Passport Image"
                  file={docFile}
                  onFile={setDocFile}
                  icon={Upload}
                />
                {docFile && (
                  <button className="clear-btn" onClick={() => setDocFile(null)}>
                    <X size={14} /> Remove
                  </button>
                )}
              </div>

              <div className="upload-col">
                <div className="upload-col-header">
                  <Camera size={18} />
                  <span>Verification Photo <span className="optional-badge">Optional</span></span>
                </div>
                <DropZone
                  id="face-upload"
                  label="Upload Selfie / Photo"
                  file={faceFile}
                  onFile={setFaceFile}
                  icon={Camera}
                />
                {faceFile && (
                  <button className="clear-btn" onClick={() => setFaceFile(null)}>
                    <X size={14} /> Remove
                  </button>
                )}
              </div>
            </div>

            <motion.button
              className="screen-btn"
              disabled={!docFile}
              onClick={handleScreen}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <ScanLine size={20} />
              Start AI Screening
            </motion.button>

            {!docFile && (
              <p className="upload-hint-text">Upload a passport document image to begin screening.</p>
            )}
          </motion.div>
        )}

        {/* SCANNING STEP */}
        {step === "scanning" && (
          <motion.div
            key="scanning"
            className="scanning-section"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="scanning-ring">
              <Loader2 size={48} className="scanning-spinner" />
              <div className="scanning-pulse" />
            </div>
            <h2 className="scanning-title">AI Analysis in Progress</h2>
            <p className="scanning-step-text">
              {scanSteps[Math.min(stepIndex, scanSteps.length - 1)]}
            </p>
            <div className="progress-bar-track">
              <motion.div
                className="progress-bar-fill"
                style={{ width: `${scanProgress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
            <span className="progress-pct">{Math.round(scanProgress)}%</span>
          </motion.div>
        )}

        {/* ERROR STEP */}
        {step === "error" && (
          <motion.div
            key="error"
            className="error-section"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <AlertCircle size={48} className="text-red-400" />
            <h2 className="error-title">Screening Failed</h2>
            <p className="error-message">{error}</p>
            <p className="error-hint">Make sure the FastAPI backend is running at <code>http://localhost:8000</code></p>
            <button className="reset-btn" onClick={reset}>Try Again</button>
          </motion.div>
        )}

        {/* RESULTS STEP */}
        {step === "results" && result && (
          <motion.div
            key="results"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="results-toolbar">
              <h2 className="results-title">Screening Complete</h2>
              <button className="reset-btn" onClick={reset}>
                <ScanLine size={16} /> New Screening
              </button>
            </div>
            <ResultPanel result={result} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
