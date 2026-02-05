"use client";
import React, { useState } from "react";

interface DraftProps {
  handleStartDraft: (query: string) => void;
  loading: boolean;
}

const Draft = ({ handleStartDraft, loading }: DraftProps) => {
  const [query, setQuery] = useState("");
  return (
    <div
      className="
            bg-white rounded-2xl p-8 space-y-6
            shadow-[0_30px_80px_rgba(0,0,0,0.12)]
          "
    >
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-semibold text-gray-900">Draft Document</h1>
        <p className="text-sm text-gray-500">
          Describe what you want to draft and we’ll structure it for you
        </p>
      </div>

      <textarea
        className="
                w-full min-h-40 rounded-xl
                border border-gray-300
                p-5 text-lg leading-relaxed resize-none
                focus:outline-none focus:ring-2 focus:ring-indigo-500
                placeholder:text-gray-400
              "
        placeholder="e.g. Draft a notice to insurer in India..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      <button
        onClick={() => handleStartDraft(query)}
        className="
                inline-flex items-center justify-center gap-1
    rounded-lg bg-indigo-600 px-4 py-2
    text-sm font-medium text-white
    transition
    hover:bg-indigo-500
    disabled:cursor-not-allowed
    disabled:opacity-70
              "
      >
        {loading ? (
          <>
            Drafting <LoadingDots />
          </>
        ) : (
          "Start Draft"
        )}
      </button>

      {loading && (
        <p className="text-xs text-gray-500">
          This usually takes a few seconds...
        </p>
      )}
    </div>
  );
};

function LoadingDots() {
  return (
    <span className="inline-flex items-center gap-0.5">
      <span className="animate-bounce [animation-delay:-0.3s]">.</span>
      <span className="animate-bounce [animation-delay:-0.15s]">.</span>
      <span className="animate-bounce">.</span>
    </span>
  );
}
export default Draft;
