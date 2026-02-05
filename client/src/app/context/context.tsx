"use client";
import React, {
  createContext,
  useContext,
  useRef,
  useState,
  ReactNode,
} from "react";

/* =======================
   Types
======================= */

type ToastType = "info" | "success" | "error" | "warning";
type ToastId = string;

interface Toast {
  id: ToastId;
  message: string;
  type: ToastType;
}

interface ToastContextValue {
  addToast: (message: string, type?: ToastType) => void;
}

/* =======================
   Context
======================= */

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

export const useToast = (): ToastContextValue => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a Provider");
  }
  return context;
};

/* =======================
   Provider
======================= */

export const Provider = ({ children }: { children: ReactNode }) => {
  const [toast, setToast] = useState<Toast[]>([]);
  const timerRef = useRef<Record<ToastId, ReturnType<typeof setTimeout>>>({});

  const handleClose = (id: ToastId) => {
    const timer = timerRef.current[id];
    if (timer) {
      clearTimeout(timer);
      delete timerRef.current[id];
    }

    setToast((prev) => prev.filter((t) => t.id !== id));
  };

  const addToast = (message: string, type: ToastType = "info") => {
    const id: ToastId = crypto.randomUUID();

    setToast((prev) => [...prev, { id, message, type }]);

    timerRef.current[id] = setTimeout(() => handleClose(id), 4000);
  };

  const toastStyles: Record<ToastType, string> = {
    info: "bg-blue-500",
    success: "bg-green-500",
    error: "bg-red-500",
    warning: "bg-yellow-500",
  };

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}

      {/* Toast container */}
      <div className="fixed top-4 right-4 z-50 flex flex-col gap-3">
        {toast.map(({ id, message, type }) => (
          <div
            key={id}
            className={`flex items-center justify-between gap-4
              min-w-65 max-w-sm
              px-4 py-3 rounded-lg shadow-lg text-white
              toast-slide-in 
              ${toastStyles[type]}
            `}
          >
            <span className="text-sm font-medium">{message}</span>

            <button
              onClick={() => handleClose(id)}
              className="text-white/80 hover:text-white transition"
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};
