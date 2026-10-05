import React from 'react';
import { Link } from 'react-router-dom';
import { Activity } from 'lucide-react';

const NotFound = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[var(--color-bg-light)] p-4 text-center">
      <div className="bg-[var(--color-primary-purple)] p-3 rounded-xl text-white mb-6">
        <Activity size={48} />
      </div>
      <h1 className="text-6xl font-bold text-slate-800 mb-2">404</h1>
      <h2 className="text-2xl font-semibold text-slate-600 mb-4">Page Not Found</h2>
      <p className="text-slate-500 max-w-md mb-8">
        The page you are looking for doesn't exist or has been moved.
      </p>
      <Link to="/dashboard" className="btn-primary">
        Return to Dashboard
      </Link>
    </div>
  );
};

export default NotFound;
