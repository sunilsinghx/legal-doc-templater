"use client";

import { useState, useRef } from "react";
import ReactMarkDown from "react-markdown";

export function DraftResult({ output }: { output: string }) {
  const [copied, setCopied] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);

  async function handleCopy() {
    await navigator.clipboard.writeText(output);
    setCopied(true);
    setTimeout(() => setCopied(false), 1000);
  }

  async function handleDownloadPDF() {
    if (!contentRef.current) return;

    const html2pdf = (await import("html2pdf.js")).default;

    html2pdf()
      .set({
        margin: 0.6,
        filename: "document.pdf",
        image: { type: "jpeg", quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: "in", format: "letter", orientation: "portrait" },
      })
      .from(contentRef.current)
      .save();
  }

  return (
    <div className="h-full flex flex-col bg-white border border-gray-200 rounded-2xl shadow-md">
      {/* Toolbar — fixed height */}
      <div className="shrink-0 flex items-center justify-end gap-2  px-3 py-2 ">
        <button
          onClick={handleCopy}
          className="text-xs px-3 py-1.5 rounded-lg bg-indigo-600 text-white hover:bg-indigo-500 transition"
        >
          {copied ? "✓ Copied" : "Copy"}
        </button>

        <button
          onClick={handleDownloadPDF}
          className="text-xs px-3 py-1.5 rounded-lg bg-white border border-gray-200 hover:bg-gray-100 transition"
        >
          PDF
        </button>
      </div>

      {/* ✅ SCROLL CONTAINER */}
      <div
        ref={contentRef}
        className="
       pdf-safe
    border border-gray-200
    rounded-2xl
    whitespace-pre-wrap
    flex-1 overflow-y-auto
    px-4 py-4 sm:px-8 sm:py-6
    prose prose-slate max-w-none
    text-sm sm:text-base
    prose-pre:overflow-x-auto
      "
      >
        <ReactMarkDown>{output}</ReactMarkDown>
      </div>
    </div>
  );
}
