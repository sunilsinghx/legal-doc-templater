"use client";

import { useState } from "react";

type ChatBubbleProps = {
  message: {
    role: "system" | "user";
    text: string;
    key?: string;
  };
  onEdit: (newText: string) => void;
};

export default function ChatBubble({ message, onEdit }: ChatBubbleProps) {
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(message.text);

  // Max width for readability
  const maxWidthClass = "max-w-[75%] sm:max-w-[60%]";

  if (message.role === "system") {
    return (
      <div
        className={`bg-gray-100 text-gray-800 px-4 py-2 rounded-xl ${maxWidthClass} wrap-break-word`}
      >
        {message.text}
      </div>
    );
  }

  return (
    <div
      className={`ml-auto bg-blue-600 text-white p-3 rounded-lg relative ${maxWidthClass} wrap-break-word group`}
    >
      {editing ? (
        <div className="flex items-center gap-2">
          <input
            className="flex-1 rounded-lg px-3 py-1.5 text-sm text-white outline-none"
            value={value}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                onEdit(value);
                setEditing(false);
              }
            }}
            onChange={(e) => setValue(e.target.value)}
          />
          <button
            className="text-xs font-medium px-3 py-1.5 rounded-lg bg-gray-900 text-white hover:bg-gray-800 active:scale-[0.97] transition-all"
            onClick={() => {
              onEdit(value);
              setEditing(false);
            }}
          >
            Save
          </button>
        </div>
      ) : (
        <>
          <span className="whitespace-pre-wrap wrap-break-word">
            {message.text}
          </span>
          <button
            className="absolute -left-7 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 text-xs text-gray-300 hover:text-white transition"
            title="Edit message"
            onClick={() => setEditing(true)}
          >
            ✏️
          </button>
        </>
      )}
    </div>
  );
}
