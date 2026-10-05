import React from 'react';

export const StatCardSkeleton = () => (
  <div className="card p-5 animate-pulse border border-slate-100">
    <div className="flex justify-between items-start mb-4">
      <div className="space-y-2 flex-1">
        <div className="h-3 bg-slate-200 rounded w-24"></div>
        <div className="h-7 bg-slate-200 rounded w-16"></div>
      </div>
      <div className="w-10 h-10 bg-slate-200 rounded-xl"></div>
    </div>
    <div className="h-3 bg-slate-200 rounded w-32 mt-3"></div>
  </div>
);

export const TableSkeleton = ({ rows = 5 }) => (
  <div className="w-full animate-pulse space-y-3">
    <div className="h-10 bg-slate-100 rounded-xl w-full"></div>
    {Array.from({ length: rows }).map((_, i) => (
      <div key={i} className="h-14 bg-slate-50 rounded-xl w-full flex items-center px-4 gap-4">
        <div className="h-4 bg-slate-200 rounded w-1/4"></div>
        <div className="h-4 bg-slate-200 rounded w-1/4"></div>
        <div className="h-4 bg-slate-200 rounded w-1/4"></div>
        <div className="h-4 bg-slate-200 rounded w-1/4"></div>
      </div>
    ))}
  </div>
);

export const ChartSkeleton = () => (
  <div className="card p-6 animate-pulse border border-slate-100 h-80 flex flex-col justify-between">
    <div className="h-5 bg-slate-200 rounded w-48 mb-4"></div>
    <div className="flex-1 bg-slate-100 rounded-xl w-full flex items-end p-4 gap-4">
      <div className="h-2/3 bg-slate-200 rounded flex-1"></div>
      <div className="h-4/5 bg-slate-200 rounded flex-1"></div>
      <div className="h-1/2 bg-slate-200 rounded flex-1"></div>
      <div className="h-3/4 bg-slate-200 rounded flex-1"></div>
    </div>
  </div>
);

export const CardSkeleton = StatCardSkeleton;

export const Skeleton = ({ className = "h-40" }) => (
  <div className={`animate-pulse bg-slate-200/80 rounded-xl ${className}`}></div>
);

export default Skeleton;
