import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import PageHeader from '../components/PageHeader';
import StatCard from '../components/StatCard';
import { StatCardSkeleton, TableSkeleton, ChartSkeleton } from '../components/Skeleton';
import ErrorState from '../components/ErrorState';
import { Activity, Camera, BrainCircuit, HeartPulse, FileImage, ShieldCheck } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { Link } from 'react-router-dom';
import api from '../services/api';
import eventBus from '../utils/eventBus';

const Dashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [dashboardStats, setDashboardStats] = useState({
    totalScans: 0,
    xrayScans: 0,
    ctScans: 0,
    mriScans: 0,
    ultrasoundScans: 0,
    totalPatients: 0,
    totalReports: 0,
    emergencyCases: 0,
    recentScans: []
  });

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/dashboard/stats');
      setDashboardStats(response.data);
    } catch (err) {
      console.error("Failed to fetch dashboard stats", err);
      setError(err?.message || "Failed to load dashboard metrics");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const unsubscribe = eventBus.on('refreshData', fetchStats);
    return () => unsubscribe();
  }, []);

  const stats = [
    { title: 'Total Scans', value: dashboardStats.totalScans || 0, icon: <Camera size={22} />, color: '#6C4CF5' },
    { title: 'X-Ray Count', value: dashboardStats.xrayScans || 0, icon: <FileImage size={22} />, color: '#60A5FA' },
    { title: 'CT Count', value: dashboardStats.ctScans || 0, icon: <HeartPulse size={22} />, color: '#4ADE80' },
    { title: 'MRI Count', value: dashboardStats.mriScans || 0, icon: <BrainCircuit size={22} />, color: '#F472B6' },
    { title: 'Ultrasound Count', value: dashboardStats.ultrasoundScans || 0, icon: <Activity size={22} />, color: '#F59E0B' },
    { title: 'Total Patients', value: dashboardStats.totalPatients || 0, icon: <ShieldCheck size={22} />, color: '#10B981' },
    { title: 'Total Reports', value: dashboardStats.totalReports || 0, icon: <FileImage size={22} />, color: '#8B5CF6' },
  ];

  const chartData = [
    { name: 'X-Ray', value: dashboardStats.xrayScans || 0, color: '#60A5FA' },
    { name: 'CT', value: dashboardStats.ctScans || 0, color: '#4ADE80' },
    { name: 'MRI', value: dashboardStats.mriScans || 0, color: '#F472B6' },
    { name: 'Ultrasound', value: dashboardStats.ultrasoundScans || 0, color: '#F59E0B' },
  ].filter(item => item.value > 0);

  return (
    <div className="space-y-6">
      <PageHeader 
        title={`Welcome back, ${user?.fullName || 'Doctor'}`}
        subtitle="Here's what's happening in your diagnostic center today."
        action={
          <Link to="/upload" className="btn-primary shadow-sm hover:shadow">
            <Activity size={18} />
            <span>New Analysis</span>
          </Link>
        }
      />

      {error ? (
        <ErrorState title="Unable to load dashboard metrics" message={error} onRetry={fetchStats} />
      ) : (
        <>
          {/* Stats Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {loading ? (
              Array.from({ length: 7 }).map((_, idx) => <StatCardSkeleton key={idx} />)
            ) : (
              stats.map((stat, idx) => (
                <StatCard 
                  key={idx}
                  title={stat.title}
                  value={stat.value}
                  icon={stat.icon}
                  accentColor={stat.color}
                  delay={idx * 40}
                />
              ))
            )}
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
            
            {/* Recent Scans Table */}
            {user?.preferences?.dashboard?.showRecentScans !== false && (
              <div className="xl:col-span-2 card p-6">
                <div className="flex justify-between items-center mb-6">
                  <div>
                    <h3 className="text-lg font-bold text-slate-800">Recent Scans</h3>
                    <p className="text-xs text-slate-500 mt-0.5">Latest imaging requests processed by AI engine</p>
                  </div>
                  <Link to="/reports" className="text-sm font-semibold text-[var(--color-primary-purple)] hover:underline">
                    View All
                  </Link>
                </div>
                
                {loading ? (
                  <TableSkeleton rows={4} />
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="border-b border-slate-200/80 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                          <th className="pb-3">Patient Name</th>
                          <th className="pb-3">Scan Type</th>
                          <th className="pb-3">Date</th>
                          <th className="pb-3 text-right">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 text-sm">
                        {dashboardStats.recentScans && dashboardStats.recentScans.length > 0 ? (
                          dashboardStats.recentScans.map((scan, idx) => (
                            <tr key={idx} className="hover:bg-slate-50/80 transition-colors group">
                              <td className="py-3.5 font-semibold text-slate-800">{scan.patientName}</td>
                              <td className="py-3.5 text-slate-600 font-medium">
                                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 text-xs font-bold uppercase">
                                  {scan.scanType}
                                </span>
                              </td>
                              <td className="py-3.5 text-slate-500 text-xs">
                                {new Date(scan.date || scan.uploadedAt).toLocaleDateString(undefined, {
                                  year: 'numeric', month: 'short', day: 'numeric'
                                })}
                              </td>
                              <td className="py-3.5 text-right">
                                <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${
                                  scan.status === 'COMPLETED' 
                                    ? 'bg-emerald-50 text-emerald-700 border-emerald-200/80' 
                                    : 'bg-blue-50 text-blue-700 border-blue-200/80'
                                }`}>
                                  {scan.status}
                                </span>
                              </td>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td colSpan="4" className="py-10 text-center">
                              <div className="flex flex-col items-center justify-center text-slate-400">
                                <Camera size={40} className="mb-2 opacity-30" />
                                <p className="text-sm font-medium text-slate-500">No recent scans found</p>
                              </div>
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {/* Distribution Chart */}
            {user?.preferences?.dashboard?.showScanDistribution !== false && (
              <div className="card p-6 flex flex-col justify-between">
                <div>
                  <h3 className="text-lg font-bold text-slate-800">Scan Distribution</h3>
                  <p className="text-xs text-slate-500 mt-0.5">Breakdown by imaging modality</p>
                </div>
                
                {loading ? (
                  <ChartSkeleton />
                ) : (
                  <div className="h-[250px] flex items-center justify-center my-auto">
                    {chartData.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie 
                            data={chartData} 
                            innerRadius={55} 
                            outerRadius={80} 
                            paddingAngle={4} 
                            dataKey="value"
                            animationDuration={600}
                          >
                            {chartData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <Tooltip 
                            contentStyle={{ borderRadius: '12px', border: '1px solid #E2E8F0', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }} 
                          />
                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="text-center text-slate-400 my-auto">
                        <Camera size={40} className="mx-auto mb-2 opacity-30" />
                        <p className="text-sm font-medium text-slate-500">No scan distribution data</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard;
