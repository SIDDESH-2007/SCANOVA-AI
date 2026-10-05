import React from 'react';
import AnimatedCounter from './AnimatedCounter';

const StatCard = ({ title, value, icon, trend, accentColor = "#6C4CF5", delay = 0 }) => {
  return (
    <div 
      className="card-hover p-5 flex flex-col justify-between group animate-slide-up-sm"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex justify-between items-start mb-3">
        <div>
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">{title}</p>
          <h3 className="text-2xl font-bold text-slate-800 tracking-tight">
            <AnimatedCounter value={value} />
          </h3>
        </div>
        <div 
          className="p-3 rounded-xl transition-transform duration-200 group-hover:scale-105" 
          style={{ backgroundColor: `${accentColor}18`, color: accentColor }}
        >
          {icon}
        </div>
      </div>
      {trend && (
        <div className="flex items-center text-xs font-medium pt-2 border-t border-slate-100/60 mt-1">
          <span className={trend.isPositive ? 'text-emerald-600 font-semibold' : 'text-rose-500 font-semibold'}>
            {trend.value}
          </span>
          <span className="text-slate-400 ml-1.5 font-normal">{trend.label}</span>
        </div>
      )}
    </div>
  );
};

export default StatCard;
