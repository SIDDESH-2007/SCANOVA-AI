import React from 'react';

const PageHeader = ({ title, subtitle, action }) => {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">{title}</h1>
        {subtitle && <p className="text-slate-500 mt-1">{subtitle}</p>}
      </div>
      {action && (
        <div>
          {action}
        </div>
      )}
    </div>
  );
};

export default PageHeader;
