"use client";

export default function VarsPanel({ variables, prefilled, answers }: any) {
  const filled = { ...prefilled, ...answers };

  return (
    <div
      className="
      max-h-70 overflow-y-auto
      bg-white
      rounded-xl
      border border-gray-200
      shadow-lg
    "
    >
      {/* Header */}
      <div className="px-4 py-2  bg-gray-50">
        <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wide">
          Variables
        </h3>
      </div>

      {/* List */}
      <div className="px-4 py-3 space-y-3">
        {variables.map((key: string) => {
          const value = filled[key];
          const isFilled = value !== undefined && value !== "";

          return (
            <div
              key={key}
              className="
              flex flex-col gap-1
              rounded-lg px-3 py-2
              bg-gray-50
            "
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-800">{key}</span>

                <span
                  className={`
                  text-xs font-medium px-2 py-0.5 rounded-full
                  ${
                    isFilled
                      ? "bg-emerald-100 text-emerald-700"
                      : "bg-rose-100 text-rose-700"
                  }
                `}
                >
                  {isFilled ? "Filled" : "Missing"}
                </span>
              </div>

              <div className="text-xs text-gray-600 truncate">
                {isFilled ? value : "No value provided"}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
