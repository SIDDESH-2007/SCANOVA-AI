import React, { useState, useEffect } from 'react';
import PageHeader from '../components/PageHeader';
import StatCard from '../components/StatCard';
import { Camera, AlertTriangle, ShieldCheck, ActivitySquare } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, Legend, PieChart, Pie, Cell } from 'recharts';
import api from '../services/api';
import eventBus from '../utils/eventBus';
import { CardSkeleton } from '../components/Skeleton';

const Analytics = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await api.get('/analytics/summary');
        setAnalyticsData(response.data);
      } catch (error) {
        console.error("Failed to fetch analytics summary", error);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
    
    const unsubscribe = eventBus.on('refreshData', fetchAnalytics);
    return () => unsubscribe();
  }, []);

  const totalMonthlyScans = analyticsData?.monthlyScanTrend?.[0]?.scans || 0;
  const highConfidenceCount = analyticsData?.confidenceDistribution?.find(c => c.name === "High Model Confidence")?.value || 0;

  const stats = [
    { title: 'Total Scans (Month)', value: totalMonthlyScans.toString(), icon: <Camera size={22} />, color: '#6C4CF5' },
    { title: 'Positive Findings', value: (analyticsData?.findingDistribution?.filter(f => f.name !== 'Normal' && f.name !== 'No Data').reduce((acc, curr) => acc + curr.value, 0) || 0).toString(), icon: <ActivitySquare size={22} />, color: '#EF4444' },
    { title: 'High Confidence Scans', value: highConfidenceCount.toString(), icon: <ShieldCheck size={22} />, color: '#22C55E' },
    { title: 'Emergency Cases', value: (analyticsData?.emergencyVsNormal?.find(e => e.name === 'Emergency')?.value || 0).toString(), icon: <AlertTriangle size={22} />, color: '#F59E0B' },
  ];

  const COLORS = ['#6C4CF5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

  return (
    <div className="space-y-6 fade-in">
      <PageHeader 
        title="Analytics Overview"
        subtitle="Monitor diagnostic performance and scan statistics in real time."
      />

      {/* Top Stats */}
      {loading ? (
        <CardSkeleton count={4} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, idx) => (
            <StatCard 
              key={idx}
              title={stat.title}
              value={stat.value}
              icon={stat.icon}
              accentColor={stat.color}
              delayClass={`stagger-${idx + 1}`}
            />
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Chart 1: Scans Over Time */}
        <div className="card p-6 card-hover stagger-1">
          <h3 className="text-base font-bold text-slate-800 mb-6 flex items-center justify-between">
            <span>Daily Scan Volume</span>
            <span className="text-xs font-semibold text-slate-400 bg-slate-100 px-2.5 py-1 rounded-full">Last 30 Days</span>
          </h3>
          <div className="h-64">
            {loading ? (
              <div className="w-full h-full bg-slate-50 rounded-xl animate-pulse"></div>
            ) : analyticsData?.dailyScanTrend && analyticsData.dailyScanTrend.length > 0 && analyticsData.dailyScanTrend[0].date !== "No Data" ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={analyticsData.dailyScanTrend} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorScans" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6C4CF5" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#6C4CF5" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: '#64748B', fontSize: 11}} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748B', fontSize: 11}} />
                  <RechartsTooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }} />
                  <Area type="monotone" dataKey="scans" stroke="#6C4CF5" strokeWidth={3} fillOpacity={1} fill="url(#colorScans)" isAnimationActive={true} animationDuration={600} />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 flex-col">
                <Camera size={40} className="mb-2 opacity-20" />
                <p className="text-xs font-medium text-slate-500">No scan trend data recorded yet.</p>
              </div>
            )}
          </div>
        </div>

        {/* Chart 2: Scan Type Distribution */}
        <div className="card p-6 card-hover stagger-2">
          <h3 className="text-base font-bold text-slate-800 mb-6 flex items-center justify-between">
            <span>Modality Breakdown</span>
            <span className="text-xs font-semibold text-slate-400 bg-slate-100 px-2.5 py-1 rounded-full">All Time</span>
          </h3>
          <div className="h-64">
            {loading ? (
              <div className="w-full h-full bg-slate-50 rounded-xl animate-pulse"></div>
            ) : analyticsData?.scanTypeDistribution && analyticsData.scanTypeDistribution.some(s => s.value > 0) ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analyticsData.scanTypeDistribution} margin={{ top: 20, right: 20, left: -20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748B', fontSize: 11}} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748B', fontSize: 11}} />
                  <RechartsTooltip cursor={{fill: '#F1F5F9'}} contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }} />
                  <Bar dataKey="value" fill="#10B981" radius={[6, 6, 0, 0]} isAnimationActive={true} animationDuration={600} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 flex-col">
                <BarChart size={40} className="mb-2 opacity-20" />
                <p className="text-xs font-medium text-slate-500">No scan distribution data available.</p>
              </div>
            )}
          </div>
        </div>

        {/* Chart 3: Prediction Distribution */}
        <div className="card p-6 card-hover stagger-3">
          <h3 className="text-base font-bold text-slate-800 mb-6">Diagnostic Findings Distribution</h3>
          <div className="h-64">
            {loading ? (
              <div className="w-full h-full bg-slate-50 rounded-xl animate-pulse"></div>
            ) : analyticsData?.findingDistribution && analyticsData.findingDistribution[0].name !== "No Data" ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={analyticsData.findingDistribution} innerRadius={60} outerRadius={90} paddingAngle={5} dataKey="value" isAnimationActive={true} animationDuration={600}>
                    {analyticsData.findingDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip contentStyle={{ borderRadius: '12px', border: 'none' }} />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 flex-col">
                <ActivitySquare size={40} className="mb-2 opacity-20" />
                <p className="text-xs font-medium text-slate-500">No clinical findings distribution recorded.</p>
              </div>
            )}
          </div>
        </div>

        {/* Chart 4: Case Priority */}
        <div className="card p-6 card-hover stagger-4">
          <h3 className="text-base font-bold text-slate-800 mb-6">Case Priority Distribution</h3>
          <div className="h-64">
            {loading ? (
              <div className="w-full h-full bg-slate-50 rounded-xl animate-pulse"></div>
            ) : analyticsData?.emergencyVsNormal && analyticsData.emergencyVsNormal.some(e => e.value > 0) ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={analyticsData.emergencyVsNormal} outerRadius={90} dataKey="value" label isAnimationActive={true} animationDuration={600}>
                    <Cell fill="#EF4444" /> {/* Emergency */}
                    <Cell fill="#6C4CF5" /> {/* Normal */}
                  </Pie>
                  <RechartsTooltip contentStyle={{ borderRadius: '12px', border: 'none' }} />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 flex-col">
                <AlertTriangle size={40} className="mb-2 opacity-20" />
                <p className="text-xs font-medium text-slate-500">No emergency priority data recorded.</p>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default Analytics;
