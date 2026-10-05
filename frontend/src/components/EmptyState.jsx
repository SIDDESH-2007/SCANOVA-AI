import React from 'react';
import { Inbox } from 'lucide-react';

const EmptyState = ({ 
  icon: Icon = Inbox, 
  title = "No Data Available", 
  message = "There are no records to display at this time.", 
  actionLabel, 
  onAction 
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-10 text-center bg-white rounded-2xl border border-slate-100 shadow-sm my-4 animate-fade-in">
      <div className="w-14 h-14 bg-slate-50 text-slate-400 rounded-2xl flex items-center justify-center mb-4 border border-slate-100 shadow-inner">
        <Icon size={28} />
      </div>
      <h3 className="text-lg font-semibold text-slate-800 mb-1">{title}</h3>
      <p className="text-sm text-slate-500 max-w-sm leading-relaxed mb-6">{message}</p>
      {actionLabel && onAction && (
        <button onClick={onAction} className="btn-primary">
          {actionLabel}
        </button>
      )}
    </div>
  );
};

export default EmptyState;
