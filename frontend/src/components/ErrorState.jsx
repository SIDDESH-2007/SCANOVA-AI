import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

const ErrorState = ({ 
  title = "Unable to Load Data", 
  message = "A network or server error occurred while retrieving data. Please check your backend connection and try again.", 
  onRetry 
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-red-50/50 rounded-2xl border border-red-100 shadow-sm my-4 animate-fade-in">
      <div className="w-12 h-12 bg-red-100 text-red-500 rounded-2xl flex items-center justify-center mb-3">
        <AlertCircle size={24} />
      </div>
      <h3 className="text-base font-semibold text-slate-800 mb-1">{title}</h3>
      <p className="text-sm text-slate-600 max-w-md mb-5 leading-relaxed">{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="btn-secondary text-sm py-2">
          <RefreshCw size={16} />
          <span>Retry</span>
        </button>
      )}
    </div>
  );
};

export default ErrorState;
