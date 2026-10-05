import React, { useState, useEffect } from 'react';
import PageHeader from '../components/PageHeader';
import { Search, Users, Eye, X, Download, Activity, FileText } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import eventBus from '../utils/eventBus';
import { TableSkeleton } from '../components/Skeleton';
import EmptyState from '../components/EmptyState';
import toast from '../utils/toast';

const Patients = () => {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [patientDetails, setPatientDetails] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);

  useEffect(() => {
    fetchPatients();
    
    const unsubscribe = eventBus.on('refreshData', fetchPatients);
    return () => unsubscribe();
  }, []);

  const fetchPatients = async () => {
    try {
      const response = await api.get('/patients');
      setPatients(response.data);
    } catch (err) {
      console.error('Failed to fetch patients', err);
      toast.error('Failed to fetch patient records');
    } finally {
      setLoading(false);
    }
  };

  const handleViewPatient = async (patientId) => {
    setSelectedPatient(patientId);
    setDetailsLoading(true);
    try {
      const response = await api.get(`/patients/${patientId}`);
      setPatientDetails(response.data);
    } catch (err) {
      console.error('Failed to fetch patient details', err);
      toast.error('Failed to load patient history');
    } finally {
      setDetailsLoading(false);
    }
  };

  const filteredPatients = patients.filter(p => 
    p.patientName?.toLowerCase().includes(search.toLowerCase()) ||
    p.patientId?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 fade-in">
      <PageHeader 
        title="Patients Directory"
        subtitle="Manage patient records and view comprehensive diagnostic scan histories."
      />

      <div className="card overflow-hidden">
        {/* Search Toolbar */}
        <div className="p-4 sm:p-6 border-b border-slate-100 flex flex-col sm:flex-row justify-between gap-4">
          <div className="relative max-w-md w-full">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input 
              type="text" 
              placeholder="Search by Patient ID or Name..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-purple)] transition-all"
            />
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left whitespace-nowrap">
            <thead className="bg-slate-50/80 border-b border-slate-100">
              <tr className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                <th className="px-6 py-4">Patient ID</th>
                <th className="px-6 py-4">Patient Name</th>
                <th className="px-6 py-4">Age</th>
                <th className="px-6 py-4">Gender</th>
                <th className="px-6 py-4">Total Scans</th>
                <th className="px-6 py-4">Last Scan Date</th>
                <th className="px-6 py-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {loading ? (
                <TableSkeleton columns={7} rows={5} />
              ) : filteredPatients.length > 0 ? (
                filteredPatients.map((patient) => (
                  <tr key={patient.patientId} className="hover:bg-purple-50/20 transition-colors duration-150">
                    <td className="px-6 py-4 font-bold text-[var(--color-primary-purple)]">{patient.patientId}</td>
                    <td className="px-6 py-4 font-semibold text-slate-800">{patient.patientName}</td>
                    <td className="px-6 py-4 text-slate-600">{patient.age}</td>
                    <td className="px-6 py-4 text-slate-600 capitalize">{patient.gender}</td>
                    <td className="px-6 py-4">
                      <span className="bg-slate-100 text-slate-700 text-xs font-bold px-2.5 py-1 rounded-full">
                        {patient.totalScans} {patient.totalScans === 1 ? 'Scan' : 'Scans'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-500 text-xs font-medium">
                      {patient.lastScanDate ? new Date(patient.lastScanDate).toLocaleDateString() : 'N/A'}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button 
                        onClick={() => handleViewPatient(patient.patientId)}
                        className="btn-secondary text-xs inline-flex items-center gap-1.5 py-1.5 px-3 bg-purple-50 text-[var(--color-primary-purple)] hover:bg-purple-100 font-semibold border border-purple-200 rounded-xl transition-all"
                      >
                        <Eye size={14} /> View History
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7" className="p-0">
                    <EmptyState 
                      icon={Users}
                      title="No patient records found"
                      description="Upload a medical scan to automatically generate a patient record."
                    />
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Patient View Modal & Scan History */}
      {selectedPatient && (
        <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 fade-in" onClick={() => { setSelectedPatient(null); setPatientDetails(null); }}>
          <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-slate-100 scale-in-small" onClick={e => e.stopPropagation()}>
            <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/80 sticky top-0 z-10 backdrop-blur-md">
              <div>
                <h3 className="text-lg font-bold text-slate-800">
                  {patientDetails ? patientDetails.patient.patientName : 'Patient Record'}
                </h3>
                <p className="text-xs font-semibold text-[var(--color-primary-purple)]">Patient ID: {selectedPatient}</p>
              </div>
              <button 
                onClick={() => { setSelectedPatient(null); setPatientDetails(null); }}
                className="p-2 text-slate-400 hover:text-slate-600 rounded-xl hover:bg-slate-200/60 transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            <div className="p-6 space-y-6">
              {detailsLoading ? (
                <div className="py-12 text-center text-slate-400 flex flex-col items-center">
                  <div className="w-8 h-8 border-4 border-slate-200 border-t-[var(--color-primary-purple)] rounded-full animate-spin mb-3"></div>
                  <p className="text-sm font-medium">Loading patient history...</p>
                </div>
              ) : patientDetails ? (
                <>
                  {/* Patient Info Summary */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 bg-purple-50/50 rounded-xl border border-purple-100 text-xs">
                    <div>
                      <p className="text-slate-500 font-medium mb-0.5">Name</p>
                      <p className="font-bold text-slate-800 text-sm">{patientDetails.patient.patientName}</p>
                    </div>
                    <div>
                      <p className="text-slate-500 font-medium mb-0.5">Age / Gender</p>
                      <p className="font-semibold text-slate-800 text-sm">{patientDetails.patient.age} / <span className="capitalize">{patientDetails.patient.gender}</span></p>
                    </div>
                    <div>
                      <p className="text-slate-500 font-medium mb-0.5">Patient ID</p>
                      <p className="font-bold text-[var(--color-primary-purple)] text-sm">{patientDetails.patient.patientId}</p>
                    </div>
                    <div>
                      <p className="text-slate-500 font-medium mb-0.5">Record Created</p>
                      <p className="font-semibold text-slate-800 text-sm">{new Date(patientDetails.patient.createdAt).toLocaleDateString()}</p>
                    </div>
                  </div>

                  {/* Scan History Section */}
                  <div>
                    <h4 className="text-base font-bold text-slate-800 mb-4 border-b border-slate-100 pb-2 flex items-center gap-2">
                      <Activity size={18} className="text-[var(--color-primary-purple)]" />
                      Diagnostic History
                    </h4>

                    {patientDetails.scanHistory && patientDetails.scanHistory.length > 0 ? (
                      <div className="space-y-4">
                        {patientDetails.scanHistory.map((scan, idx) => (
                          <div key={idx} className="border border-slate-200 rounded-xl p-4 flex flex-col md:flex-row items-center gap-4 bg-slate-50/50 hover:bg-slate-100/50 transition-colors">
                            
                            {/* Original Image Preview */}
                            <div className="w-24 h-24 bg-slate-900 rounded-xl overflow-hidden flex-shrink-0 flex items-center justify-center border border-slate-800 shadow-inner">
                              {scan.originalImage ? (
                                <img src={`http://localhost:8000${scan.originalImage}`} alt="Scan Thumbnail" className="w-full h-full object-cover" />
                              ) : (
                                <FileText className="text-slate-500" size={32} />
                              )}
                            </div>

                            {/* Details */}
                            <div className="flex-1 space-y-1 text-center md:text-left">
                              <div className="flex flex-wrap items-center justify-center md:justify-start gap-2">
                                <span className="text-[11px] bg-purple-100 text-[var(--color-primary-purple)] px-2.5 py-0.5 rounded-full font-bold uppercase">
                                  {scan.scanType}
                                </span>
                                <span className="text-xs text-slate-500 font-medium">
                                  {new Date(scan.date).toLocaleDateString()}
                                </span>
                              </div>

                              <h5 className="font-bold text-slate-800 text-sm">{scan.possibleFinding}</h5>
                              
                              <div className="flex flex-wrap items-center justify-center md:justify-start gap-4 text-xs text-slate-600">
                                <span>Confidence: <strong className="text-slate-800">{(scan.confidence * 100).toFixed(2)}%</strong></span>
                                <span>Level: <strong className="text-slate-800">{scan.confidenceLevel}</strong></span>
                                <span>Review: <strong className="text-amber-600">{scan.reviewStatus}</strong></span>
                              </div>
                            </div>

                            {/* Actions */}
                            <div className="flex flex-col gap-2 w-full md:w-auto">
                              {scan.predictionId && (
                                <Link 
                                  to={`/prediction/${scan.predictionId}`} 
                                  onClick={() => setSelectedPatient(null)}
                                  className="btn-primary text-xs text-center py-2 px-4 rounded-xl"
                                >
                                  View Result
                                </Link>
                              )}
                              {scan.reportId && (
                                <a 
                                  href={`http://localhost:8000/api/reports/${scan.reportId}/pdf`} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  download
                                  className="btn-secondary text-xs flex items-center justify-center gap-1.5 py-2 px-3 bg-white border border-slate-300 rounded-xl"
                                >
                                  <Download size={14} /> PDF Report
                                </a>
                              )}
                            </div>

                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-slate-500 text-center py-6">No scan history available for this patient.</p>
                    )}
                  </div>
                </>
              ) : (
                <p className="text-sm text-red-500 text-center py-6">Failed to load patient record.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Patients;

