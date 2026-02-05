"use client";

import { useRouter } from "next/navigation";
import FileUpload from "@/app/components/FileUpload";

export default function Page() {
  const router = useRouter();

  function handleClick() {
    router.push(`/draft`);
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-linear-to-br from-slate-100 via-gray-100 to-slate-200 px-4 py-6">
      <div className="w-full max-w-md sm:max-w-xl bg-white p-6 sm:p-8 rounded-2xl shadow-xl space-y-8">
        {/* Title */}
        <h1 className="text-2xl sm:text-3xl font-bold text-center text-gray-900">
          Legal Draft Assistant
        </h1>

        {/* Upload Section */}
        <section className="space-y-3">
          <h2 className="text-base sm:text-lg font-semibold text-gray-800">
            Upload a legal document
          </h2>
          <FileUpload />
          <p className="text-xs sm:text-sm text-gray-500">
            Upload <span className="font-mono">.pdf</span> or{" "}
            <span className="font-mono">.docx</span> to create reusable
            templates
          </p>
        </section>

        {/* Divider */}
        <div className="flex items-center justify-center text-gray-400 text-xs sm:text-sm font-medium">
          <span className="border-t border-gray-300 flex-1 mr-2"></span>
          OR
          <span className="border-t border-gray-300 flex-1 ml-2"></span>
        </div>

        {/* Draft Button */}
        <section>
          <button
            className="w-full py-3 px-5 bg-indigo-600 text-white font-medium rounded-lg shadow-md hover:bg-indigo-500 active:scale-[0.97] transition-transform text-sm sm:text-base"
            onClick={handleClick}
          >
            Draft a new document
          </button>
        </section>
      </div>
    </main>
  );
}
