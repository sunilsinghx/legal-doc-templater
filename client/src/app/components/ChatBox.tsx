"use client";

import React, { useState } from "react";

interface ChatBoxProps {
  onSend: (message: string) => void;
  showVars: boolean;
  setShowVars: (value: boolean) => void;
  children?: React.ReactNode;
}

export default function ChatBox({
  onSend,
  showVars,
  setShowVars,
  children,
}: ChatBoxProps) {
  const [input, setInput] = useState("");

  const showHint = input === "/v";
  // const [showHint, setShowHint] = useState(false);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const value = e.target.value;
    setInput(value);
    // setShowHint(value === "/v");

    if (value === "/vars") {
      setShowVars(true);
    } else if (value == "") {
      setShowVars(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (showHint && e.key === "Tab") {
      e.preventDefault();
      setInput("/vars");
      setShowVars(true);
      return;
    }

    if (e.key === "Enter") {
      e.preventDefault();
      handleSend();
    }
  }

  function handleSend() {
    if (!input.trim()) return;

    onSend(input);
    setInput("");
    setShowVars(false);
  }

  return (
    /* 🔑 RELATIVE ANCHOR */
    <div className="relative w-full">
      {/* Input container */}

      {showHint && (
        <div
          className="
         left-3 top-full mb-1
        text-xs text-gray-600
       bg-transparent
        rounded-md px-2 py-1
        z-20
      "
        >
          Press <kbd className="px-1 rounded bg-gray-100 border">Tab</kbd> to
          autocomplete <strong>/vars</strong>
        </div>
      )}
      <div
        className="
        flex items-center gap-2
        bg-gray-50 border border-gray-200
        rounded-xl px-3 py-2
        shadow-sm
        focus-within:ring-2 focus-within:ring-indigo-500
        transition
      "
      >
        {/* Text input */}
        <input
          className="
          flex-1 bg-transparent
          text-sm
          px-2 py-2
          outline-none
          placeholder:text-gray-400
        "
          placeholder='Answer or type "/vars"'
          value={input}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
        />

        {/* Send button */}
        <button
          onClick={handleSend}
          disabled={!input.trim()}
          className="
          shrink-0
          bg-indigo-600 text-white
          text-xs font-medium
          px-3 py-1.5 rounded-lg
          hover:bg-indigo-500
          active:scale-95
          transition
        "
        >
          Send
        </button>
      </div>

      {/* 🔽 VARS DROPDOWN */}
      {showVars && (
        <div
          className="
        absolute bottom-full left-0 w-full mb-2
        bg-white border border-gray-200
        rounded-xl shadow-lg
        z-50
      "
        >
          {children}
        </div>
      )}
    </div>
  );
}
