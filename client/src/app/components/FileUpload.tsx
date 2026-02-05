"use client";
import { ingestFile } from "@/app/api/api";
import { useState } from "react";
import { useToast } from "../context/context";

export default function FileUpload() {
  const [loading, setLoading] = useState(false);

  const { addToast } = useToast();

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];

    if (!file) return;
    setLoading(true);

    try {
      const res = await ingestFile(file);

      addToast("File Ingested Successfully", "success");
    } catch (error: any) {
      addToast(error.message, "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative rounded-lg border border-dashed border-gray-300 bg-gray-50 p-5 transition hover:border-gray-400">
      <label
        htmlFor="file-upload"
        className={`flex cursor-pointer flex-col items-center justify-center gap-2 text-center ${
          loading ? "cursor-not-allowed opacity-60" : ""
        }`}
      >
        {/* Icon */}
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-100">
          📄
        </div>

        {/* Text */}
        <p className="text-sm font-medium text-gray-700">
          {loading ? "Uploading document…" : "Click to upload a document"}
        </p>
        <p className="text-xs text-gray-500">PDF or DOCX files only</p>

        {/* Hidden input */}
        <input
          id="file-upload"
          type="file"
          name="file"
          accept=".pdf,.docx"
          onChange={handleUpload}
          disabled={loading}
          className="hidden"
        />
      </label>

      {/* Loading overlay */}
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center rounded-lg bg-white/70 backdrop-blur-sm">
          <div className="flex items-center gap-3 text-sm text-gray-700">
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-gray-700" />
            Processing document…
          </div>
        </div>
      )}
    </div>
  );
}
