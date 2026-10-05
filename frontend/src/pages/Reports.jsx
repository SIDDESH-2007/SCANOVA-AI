import React, { useState, useEffect } from 'react';
import PageHeader from '../components/PageHeader';
import { Search, FileText, Download, ShieldCheck, AlertTriangle, Activity } from 'lucide-react';
import api from '../services/api';
import eventBus from '../utils/eventBus';
import { TableSkeleton } from '../components/Skeleton';
import EmptyState from '../components/EmptyState';
import toast from '../utils/toast';

const Reports = () => {
  const [activeTab, setActiveTab] = useState('All Reports');
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [downloadingId, setDownloadingId] = useState(null);
  
  const tabs = ['All Reports', 'X-RAY', 'CT', 'MRI', 'ULTRASOUND'];

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const response = await api.get('/reports');
        setReports(response.data);
      } catch (err) {
        console.error("Failed to fetch reports:", err);
        toast.error("Failed to fetch diagnostic reports");
      } finally {
        setLoading(false);
      }
    };
    fetchReports();
    
    const unsubscribe = eventBus.on('refreshData', fetchReports);
    return () => unsubscribe();
  }, []);

  const handleDownloadPdf = async (reportId) => {
    setDownloadingId(reportId);
    toast.info('Preparing PDF report download...');
    try {
      const response = await api.get(`/reports/${reportId}/pdf`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const a = document.createElement('a');
      a.href = url;
      a.download = `Radiology_Report_${reportId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('PDF report download started');
    } catch (e) {
      console.error("PDF download failed:", e);
      toast.error('Failed to download PDF report. It may not exist.');
    } finally {
      setDownloadingId(null);
    }
  };

  const normalizeSearch = (query) => {
    let q = query.toUpperCase();
    if (q === 'XRAY' || q === 'X_RAY' || q === 'X RAY') return 'X-RAY';
    if (q === 'CTSCAN' || q === 'CT SCAN' || q === 'CT-SCAN') return 'CT';
    if (q === 'MRISCAN' || q === 'MRI SCAN') return 'MRI';
    if (q === 'US' || q === 'ULTRASOUND SCAN') return 'ULTRASOUND';
    return q;
  };

  const filteredReports = reports.filter(r => {
    const matchesTab = activeTab === 'All Reports' || r.scanType === activeTab;
    
    if (!searchQuery) return matchesTab;
    
    const query = searchQuery.toLowerCase();
    const normalizedQ = normalizeSearch(searchQuery);
    
    const matchesSearch = 
      (r.reportId || '').toLowerCase().includes(query) ||
      (r.patientId || '').toLowerCase().includes(query) ||
      (r.patientName || '').toLowerCase().includes(query) ||
      (r.scanType || '').toUpperCase().includes(normalizedQ) ||
      (r.possibleFinding || '').toLowerCase().includes(query) ||
      (r.reviewStatus || '').toLowerCase().includes(query);
      
    return matchesTab && matchesSearch;
  });

  return (
    <div className="space-y-6 fade-in">
      <PageHeader 
        title="Diagnostic Reports"
        subtitle="View and download AI-generated and doctor-approved PDF reports."
      />

      <div className="card overflow-hidden">
        {/* Tabs and Search */}
        <div className="p-4 sm:p-6 border-b border-slate-100 flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="flex space-x-1 bg-slate-100 p-1 rounded-xl w-full sm:w-auto overflow-x-auto">
            {tabs.map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 text-xs font-bold rounded-lg transition-all whitespace-nowrap ${
                  activeTab === tab 
                    ? 'bg-white text-[var(--color-primary-purple)] shadow-sm' 
                    : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          <div className="relative max-w-sm w-full">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input 
              type="text" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search reports..." 
              className="w-full pl-10 pr-4 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-purple)] transition-all"
            />
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left whitespace-nowrap">
            <thead className="bg-slate-50/80 border-b border-slate-100">
              <tr className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                <th className="px-6 py-4">Report ID</th>
                <th className="px-6 py-4">Patient Name</th>
                <th className="px-6 py-4">Scan Type</th>
                <th className="px-6 py-4">Case Type</th>
                <th className="px-6 py-4">AI Finding</th>
                <th className="px-6 py-4">Confidence</th>
                <th className="px-6 py-4">Generated Date</th>
                <th className="px-6 py-4">Review Status</th>
                <th className="px-6 py-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {loading ? (
                <TableSkeleton columns={9} rows={5} />
              ) : filteredReports.length === 0 ? (
                <tr>
                  <td colSpan="9" className="p-0">
                    <EmptyState 
                      icon={FileText}
                      title="No reports generated yet"
                      description="Reports will automatically appear here after medical scans are analyzed."
                    />
                  </td>
                </tr>
              ) : (
                filteredReports.map((report) => (
                  <tr key={report.reportId} className="hover:bg-purple-50/20 transition-colors duration-150">
                    <td className="px-6 py-4 font-bold text-[var(--color-primary-purple)]">{report.reportId}</td>
                    <td className="px-6 py-4 font-semibold text-slate-800">{report.patientName}</td>
                    <td className="px-6 py-4">
                      <span className="text-xs font-bold bg-purple-100 text-[var(--color-primary-purple)] px-2.5 py-1 rounded-full uppercase">
                        {report.scanType}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {report.caseType === 'EMERGENCY' ? (
                        <span className="inline-flex items-center gap-1 text-[11px] font-bold text-red-600 bg-red-50 px-2.5 py-1 rounded-full border border-red-100">
                          <AlertTriangle size={12} /> EMERGENCY
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-100">
                          <ShieldCheck size={12} /> ROUTINE
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-800">{report.possibleFinding}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-slate-100 rounded-full h-1.5 overflow-hidden">
                          <div 
                            className={`h-1.5 rounded-full transition-all duration-500 ${report.confidence > 0.89 ? 'bg-emerald-500' : report.confidence > 0.74 ? 'bg-amber-500' : 'bg-red-500'}`}
                            style={{ width: `${report.confidence * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-xs font-bold text-slate-700">{(report.confidence * 100).toFixed(1)}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-xs font-medium text-slate-500">
                      {new Date(report.createdAt).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-amber-700 bg-amber-50 px-2.5 py-1 rounded-full border border-amber-100">
                        <Activity size={12} className="animate-pulse" />
                        {report.reviewStatus}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      {report.pdfUrl ? (
                        <button 
                          onClick={() => handleDownloadPdf(report.reportId)}
                          disabled={downloadingId === report.reportId}
                          className="btn-secondary px-3 py-1.5 text-xs inline-flex items-center gap-1.5 bg-purple-50 text-[var(--color-primary-purple)] hover:bg-purple-100 border border-purple-200 rounded-xl font-bold transition-all ml-auto"
                        >
                          {downloadingId === report.reportId ? (
                            <>
                              <div className="w-3 h-3 border-2 border-[var(--color-primary-purple)] border-t-transparent rounded-full animate-spin"></div>
                              <span>Downloading...</span>
                            </>
                          ) : (
                            <>
                              <Download size={14} /> PDF
                            </>
                          )}
                        </button>
                      ) : (
                        <span className="text-xs text-slate-400">Unavailable</span>
                      )}
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

export default Reports;
