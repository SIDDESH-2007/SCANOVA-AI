import React, { useState, useEffect } from 'react';
import eventBus from '../utils/eventBus';
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';

const ToastContainer = () => {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    const handleToast = (toastData) => {
      const id = Date.now() + Math.random();
      const newToast = { id, ...toastData };
      
      setToasts((prev) => [...prev.slice(-4), newToast]);

      setTimeout(() => {
        removeToast(id);
      }, 4000);
    };

    eventBus.on('show-toast', handleToast);
    return () => {
      eventBus.off('show-toast', handleToast);
    };
  }, []);

  const removeToast = (id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-3 max-w-sm w-full pointer-events-none px-4">
      {toasts.map((toast) => {
        let icon = <CheckCircle2 className="text-emerald-500 flex-shrink-0" size={20} />;
        let borderClass = 'border-emerald-200 bg-white text-slate-800';

        if (toast.type === 'error') {
          icon = <AlertCircle className="text-red-500 flex-shrink-0" size={20} />;
          borderClass = 'border-red-200 bg-white text-slate-800';
        } else if (toast.type === 'warning') {
          icon = <AlertTriangle className="text-amber-500 flex-shrink-0" size={20} />;
          borderClass = 'border-amber-200 bg-white text-slate-800';
        } else if (toast.type === 'info') {
          icon = <Info className="text-blue-500 flex-shrink-0" size={20} />;
          borderClass = 'border-blue-200 bg-white text-slate-800';
        }

        return (
          <div
            key={toast.id}
            className={`pointer-events-auto flex items-start gap-3 p-4 rounded-xl border shadow-lg transition-all duration-300 animate-slide-up-sm ${borderClass}`}
          >
            <div className="mt-0.5">{icon}</div>
            <div className="flex-1 min-w-0">
              {toast.title && (
                <h4 className="text-sm font-semibold text-slate-800 leading-snug">{toast.title}</h4>
              )}
              <p className="text-xs text-slate-600 mt-0.5 leading-relaxed">{toast.message}</p>
            </div>
            <button
              onClick={() => removeToast(toast.id)}
              className="text-slate-400 hover:text-slate-600 p-1 rounded-lg transition-colors ml-1"
            >
              <X size={16} />
            </button>
          </div>
        );
      })}
    </div>
  );
};

export default ToastContainer;
