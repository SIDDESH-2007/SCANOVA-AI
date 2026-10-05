import React, { useState, useEffect } from 'react';
import PageHeader from '../components/PageHeader';
import { AlertTriangle, Siren, Clock, Activity, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { TableSkeleton } from '../components/Skeleton';
import EmptyState from '../components/EmptyState';
import toast from '../utils/toast';

const Emergency = () => {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCases = async () => {
      try {
        const response = await api.get('/emergency');
        setCases(response.data);
      } catch (err) {
        console.error("Failed to fetch emergency cases:", err);
        toast.error("Failed to load emergency priority queue");
      } finally {
        setLoading(false);
      }
    };
    fetchCases();
  }, []);

  return (
    <div className="space-y-6 fade-in">
      <PageHeader 
        title="Emergency Cases"
        subtitle="Manage and prioritize critical diagnostic cases requiring immediate clinical review."
      />

      <div className="card border-t-4 border-t-red-500 overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-100 flex justify-between items-center bg-red-50/20">
          <div className="flex items-center gap-2.5">
            <div className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
            </div>
            <h3 className="font-bold text-slate-800 text-base">Priority Queue</h3>
          </div>
          <div className="bg-red-100 text-red-700 font-bold px-3 py-1 rounded-full text-xs uppercase tracking-wide">
            {cases.length} {cases.length === 1 ? 'Case' : 'Cases'} Active
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left whitespace-nowrap">
            <thead className="bg-slate-50/80 border-b border-slate-100">
              <tr className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                <th className="px-6 py-4">Patient</th>
                <th className="px-6 py-4">Scan Type</th>
                <th className="px-6 py-4">Possible Condition</th>
                <th className="px-6 py-4">Priority Level</th>
                <th className="px-6 py-4">Time Flagged</th>
                <th className="px-6 py-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {loading ? (
                <TableSkeleton columns={6} rows={4} />
              ) : cases.length === 0 ? (
                <tr>
                  <td colSpan="6" className="p-0">
                    <EmptyState 
                      icon={AlertTriangle}
                      title="No active emergency cases"
                      description="Critical diagnostic findings flagged by AI will appear here automatically."
                    />
                  </td>
                </tr>
              ) : (
                cases.map((emg) => (
                  <tr key={emg.emergencyCaseId} className="hover:bg-red-50/30 transition-colors duration-150">
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-bold text-slate-800">{emg.patientName}</p>
                        <p className="text-xs font-semibold text-[var(--color-primary-purple)]">{emg.patientId}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-xs font-bold bg-slate-100 text-slate-700 px-2.5 py-1 rounded-full uppercase">
                        {emg.scanType}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <AlertTriangle size={14} className="text-red-500 flex-shrink-0" />
                        <span className="text-sm font-bold text-red-600">{emg.possibleFinding}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="bg-red-100 text-red-700 text-[11px] font-bold px-2.5 py-1 rounded-full uppercase border border-red-200">
                        {emg.priority || 'CRITICAL'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs font-medium text-slate-500">
                      <div className="flex items-center gap-1.5">
                        <Clock size={14} className="text-slate-400" />
                        {new Date(emg.createdAt).toLocaleTimeString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link to={`/prediction/${emg.predictionId}`} className="btn-primary bg-red-600 hover:bg-red-700 text-xs inline-flex items-center justify-center gap-1.5 py-2 px-4 rounded-xl ml-auto">
                        Review Case <ArrowRight size={14} />
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Emergency;
