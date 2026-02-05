"use client";

import { useEffect, useState } from "react";
import ChatBox from "@/app/components/ChatBox";
import VarsPanel from "@/app/components/VarsPanel";
import { DraftResult } from "@/app/components/DraftResult";
import { finishDraft, startDraft } from "@/app/api/api";
import ChatBubble from "../components/ChatBubble";
import Link from "next/link";
import Draft from "../components/Draft";
import { useToast } from "../context/context";

type Message = {
  role: "system" | "user";
  text: string;
  key?: string; // variable key for user answers
};

type DraftData = {
  template_id: number;
  questions: Record<string, string>;
  missing_keys: string[];
  prefilled?: Record<string, string>;
};

type FinalDoc = {
  output: string;
};

export default function Page() {
  const { addToast } = useToast();

  const [draftData, setDraftData] = useState<DraftData | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showVars, setShowVars] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [finalDoc, setFinalDoc] = useState<FinalDoc | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const questions = Object.entries(draftData?.questions || {});

  async function handleStartDraft(query: string) {
    if (!query.trim()) return;
    setLoading(true);

    try {
      const res = await startDraft(query);

      setDraftData(res);
      setAnswers({});
      setMessages([]);
      setCurrentIndex(0);
      setFinalDoc(null);

      if (res?.questions != null) {
        const [, firstQuestion]: any = Object.entries(res?.questions)[0];
        setMessages([{ role: "system", text: firstQuestion }]);
      }
    } catch (error: any) {
      addToast(error.message, "error");
    } finally {
      setLoading(false);
    }
  }

  async function handleUserMessage(text: string) {
    if (!questions[currentIndex]) return;
    if (!draftData) return;

    const [key] = questions[currentIndex];

    const nextAnswers = { ...answers, [key]: text };
    setAnswers(nextAnswers);
    setMessages((m) => [...m, { role: "user", text, key }]);

    const nextIndex = currentIndex + 1;

    if (questions[nextIndex]) {
      const [, nextQuestion] = questions[nextIndex];
      setCurrentIndex(nextIndex);
      setMessages((m: any) => [...m, { role: "system", text: nextQuestion }]);
    } else {
      try {
        setIsGenerating(true);
        const res = await finishDraft({
          template_id: draftData?.template_id,
          answers: nextAnswers,
          prefilled: draftData?.prefilled || {},
        });
        setFinalDoc(res);

        addToast("Document Drafted Successfully.", "success");
      } catch (error: any) {
        addToast(error.message, "error");
      } finally {
        setIsGenerating(false);
      }
    }
  }

  function handleEditMessage(index: number, newText: string) {
    setMessages((prev) =>
      prev.map((msg, i) => (i === index ? { ...msg, text: newText } : msg))
    );

    const msg = messages[index];
    if (msg?.key) {
      setAnswers((prev) => ({
        ...prev,
        [msg.key!]: newText,
      }));
    }

    addToast("Answer edited.", "info");
  }

  return (
    <>
      <main
        className="
      min-h-screen flex items-center justify-center p-6
      bg-linear-to-r from-slate-100 via-gray-100 to-slate-200
    "
      >
        <div className="w-full max-w-2xl">
          {!draftData ? (
            /* ---------- START SCREEN ---------- */
            <Draft loading={loading} handleStartDraft={handleStartDraft} />
          ) : (
            /* ---------- CHAT / RESULT ---------- */
            <div
              className="
            h-[90vh] w-full bg-white rounded-2xl
            shadow-xl flex flex-col overflow-hidden
          "
            >
              <div className=" px-6 py-3 border-b flex items-center gap-2 text-sm">
                <Link
                  href="/"
                  className="
      inline-flex items-center gap-1
      text-gray-600
      hover:text-indigo-600
      transition
    "
                >
                  ← Back to Home
                </Link>
              </div>
              <div
                className="
              px-6 py-4 
              text-lg font-semibold text-gray-800
            "
              >
                Draft Document
              </div>

              {/* MACC */}
              {!finalDoc && (
                <div
                  className="
                  
                flex-1 overflow-y-auto px-6 py-4
                space-y-3 bg-gray-50
                overflow-visible
              "
                >
                  <div className="px-6 text-sm text-gray-500">
                    Question {currentIndex + 1} of {questions.length}
                  </div>
                  {messages.map((m, i) => (
                    <ChatBubble
                      key={i}
                      message={m}
                      onEdit={(newText: string) =>
                        handleEditMessage(i, newText)
                      }
                    />
                  ))}

                  {isGenerating && <DraftLoading />}
                </div>
              )}

              {!finalDoc && !isGenerating && (
                <div className="relative z-40 px-6 py-4 bg-white">
                  <ChatBox
                    onSend={handleUserMessage}
                    showVars={showVars}
                    setShowVars={setShowVars}
                  >
                    <VarsPanel
                      variables={draftData.missing_keys}
                      prefilled={draftData.prefilled || {}}
                      answers={answers}
                    />
                  </ChatBox>
                </div>
              )}

              {/* HERE */}

              {finalDoc?.output && (
                <>
                  <div className=" bg-white flex-1 overflow-hidden">
                    <DraftResult output={finalDoc.output} />
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </main>
    </>
  );
}

function DraftLoading() {
  return (
    <div className="absolute inset-0 z-10 flex items-center justify-center bg-white/70 backdrop-blur-sm">
      <div className="flex flex-col items-center gap-3 rounded-xl bg-white px-6 py-5 shadow-lg">
        <span className="h-6 w-6 animate-spin rounded-full border-2 border-gray-300 border-t-indigo-600" />
        <p className="text-sm font-medium text-gray-700">
          Generating your document…
        </p>
        <p className="text-xs text-gray-500">
          This usually takes a few seconds
        </p>
      </div>
    </div>
  );
}
