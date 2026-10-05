import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import { AlertCircle, CheckCircle, Activity, FileText, User, Download, ShieldCheck, AlertTriangle, Maximize2, X } from 'lucide-react';
import api from '../services/api';
import toast from '../utils/toast';
import Skeleton from '../components/Skeleton';

const Prediction = () => {
  const { predictionId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [activeTab, setActiveTab] = useState('heatmap'); // 'heatmap' or 'original' for mobile image toggle
  const [previewModalImg, setPreviewModalImg] = useState(null);

  useEffect(() => {
    const fetchPrediction = async () => {
      try {
        const response = await api.get(`/predictions/${predictionId}`);
        const result = response.data;
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchPrediction();
  }, [predictionId]);

  const handleDownloadPdf = async (reportId) => {
    setDownloadingPdf(true);
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
      toast.success('PDF Report download started');
    } catch (e) {
      console.error("PDF download failed:", e);
      toast.error('Failed to download PDF report. It may not exist.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader title="AI Analysis Result" subtitle="Loading clinical findings..." />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Skeleton className="h-96 rounded-2xl" />
            <Skeleton className="h-32 rounded-2xl" />
          </div>
          <div className="space-y-6">
            <Skeleton className="h-64 rounded-2xl" />
            <Skeleton className="h-64 rounded-2xl" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-3xl mx-auto text-center mt-12 fade-in">
        <div className="bg-red-50 text-red-600 p-8 rounded-2xl border border-red-100 shadow-sm">
          <AlertCircle size={48} className="mx-auto mb-4 opacity-50" />
          <h2 className="text-2xl font-bold mb-2">Result Unavailable</h2>
          <p className="mb-6 text-sm">{error}</p>
          <Link to="/dashboard" className="btn-primary inline-flex">Return to Dashboard</Link>
        </div>
      </div>
    );
  }

  const { prediction, patient, scan, report } = data;
  const isHighConfidence = prediction.confidenceLevel && prediction.confidenceLevel.includes('High');
  const isWarning = prediction.predictedClass === 'PNEUMONIA';
  const isEmergency = scan.caseType === 'EMERGENCY';

  const reportId = report ? report.reportId : null;

  return (
    <div className="space-y-6 fade-in">
      <PageHeader 
        title="AI Analysis Result" 
        subtitle={`Prediction ID: ${prediction.predictionId}`}
        action={
          <div className="flex flex-wrap gap-3">
            {reportId && (
              <button 
                onClick={() => handleDownloadPdf(reportId)} 
                disabled={downloadingPdf}
                className="btn-secondary flex items-center gap-2 bg-purple-50 text-[var(--color-primary-purple)] hover:bg-purple-100 font-semibold border border-purple-200 py-2.5 px-4 rounded-xl transition-all"
              >
                {downloadingPdf ? (
                  <>
                    <div className="w-4 h-4 border-2 border-[var(--color-primary-purple)] border-t-transparent rounded-full animate-spin"></div>
                    <span>Downloading...</span>
                  </>
                ) : (
                  <>
                    <Download size={18} /> DOWNLOAD PDF REPORT
                  </>
                )}
              </button>
            )}
            <Link to="/dashboard" className="btn-primary flex items-center gap-2">Back to Dashboard</Link>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Images & Explainability */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card p-6 stagger-1">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
              <h3 className="text-base font-bold text-slate-800 flex items-center gap-2">
                <Activity className="text-[var(--color-primary-purple)]" size={20} />
                EXPLAINABLE AI VISUALIZATION
              </h3>
              
              {/* Image Quality Badge */}
              {prediction.imageValidation && (
                <div className="flex items-center gap-2 text-xs bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200">
                  <span className="text-slate-500">Validation:</span>
                  <span className="font-semibold text-emerald-600">
                    {prediction.imageValidation.imageValid ? 'Valid Scan' : 'Invalid'}
                  </span>
                  <span className="text-slate-300">|</span>
                  <span className="text-slate-500">Quality:</span>
                  <span className={`font-semibold ${prediction.imageValidation.qualityStatus === 'Good' ? 'text-emerald-600' : prediction.imageValidation.qualityStatus === 'Moderate' ? 'text-amber-600' : 'text-slate-700'}`}>
                    {prediction.imageValidation.qualityStatus}
                  </span>
                </div>
              )}
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <p className="text-xs font-bold text-slate-700 uppercase tracking-wide">Original Image ({scan.scanType})</p>
                  <button 
                    onClick={() => setPreviewModalImg(`http://localhost:8000${scan.filePath}`)}
                    className="text-xs text-slate-400 hover:text-slate-600 flex items-center gap-1"
                  >
                    <Maximize2 size={12} /> Expand
                  </button>
                </div>
                <div className="bg-slate-900 rounded-xl overflow-hidden aspect-square flex items-center justify-center border border-slate-800 shadow-inner group relative cursor-pointer" onClick={() => setPreviewModalImg(`http://localhost:8000${scan.filePath}`)}>
                  <img src={`http://localhost:8000${scan.filePath}`} alt="Original Image" className="w-full h-full object-contain transition-transform duration-300 group-hover:scale-105" />
                  <div className="absolute inset-0 bg-slate-900/30 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white text-xs font-semibold gap-1">
                    <Maximize2 size={16} /> Click to View
                  </div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between items-center mb-2">
                  <p className="text-xs font-bold text-slate-700 uppercase tracking-wide">AI Heatmap (Grad-CAM)</p>
                  {prediction.gradcamPath && (
                    <button 
                      onClick={() => setPreviewModalImg(`http://localhost:8000${prediction.gradcamPath}`)}
                      className="text-xs text-slate-400 hover:text-slate-600 flex items-center gap-1"
                    >
                      <Maximize2 size={12} /> Expand
                    </button>
                  )}
                </div>
                <div className="bg-slate-900 rounded-xl overflow-hidden aspect-square flex items-center justify-center border border-slate-800 shadow-inner group relative cursor-pointer" onClick={() => prediction.gradcamPath && setPreviewModalImg(`http://localhost:8000${prediction.gradcamPath}`)}>
                  {prediction.gradcamPath ? (
                    <>
                      <img src={`http://localhost:8000${prediction.gradcamPath}`} alt="AI Heatmap" className="w-full h-full object-contain transition-transform duration-300 group-hover:scale-105" />
                      <div className="absolute inset-0 bg-slate-900/30 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white text-xs font-semibold gap-1">
                        <Maximize2 size={16} /> Click to View
                      </div>
                    </>
                  ) : (
                    <div className="text-center p-4 text-white">
                      <AlertCircle className="mx-auto mb-2 text-slate-400" size={32} />
                      <p className="text-xs text-slate-400">Grad-CAM visualization unavailable.</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Explanation Section */}
          <div className="card p-6 border-l-4 border-l-[var(--color-primary-purple)] stagger-2">
            <h3 className="text-xs font-bold text-slate-800 mb-2 uppercase tracking-wider">WHY DID THE AI PRODUCE THIS RESULT?</h3>
            <p className="text-slate-700 leading-relaxed text-sm bg-purple-50/50 p-4 rounded-xl border border-purple-100">
              {prediction.possibleCause || "The model analyzed pattern densities within the uploaded scan."}
            </p>
          </div>
          
          <div className="bg-amber-50/80 border border-amber-200 rounded-xl p-4 flex gap-3 text-xs text-amber-900 leading-relaxed stagger-3">
            <AlertCircle size={20} className="flex-shrink-0 mt-0.5 text-amber-600" />
            <div>
              <p className="font-bold mb-0.5">Clinical Safety Disclaimer</p>
              <p>This report contains AI-generated clinical decision support information. It is not a final medical diagnosis. Final interpretation must be performed by a qualified healthcare professional. <strong>Model confidence does not represent clinical certainty.</strong></p>
            </div>
          </div>
        </div>

        {/* Prediction Details Sidebar */}
        <div className="space-y-6">
          
          {/* Main Finding Card */}
          <div className="card p-0 overflow-hidden stagger-1">
            <div className={`p-6 ${isWarning ? 'bg-amber-600' : 'bg-emerald-600'} text-white text-center transition-colors duration-300`}>
              {isWarning ? (
                <AlertCircle size={48} className="mx-auto mb-3 opacity-90 scale-in-small" />
              ) : (
                <CheckCircle size={48} className="mx-auto mb-3 opacity-90 scale-in-small" />
              )}
              <span className="text-[11px] font-bold uppercase tracking-wider bg-white/20 px-3 py-1 rounded-full inline-block mb-2">Possible Finding</span>
              <h2 className="text-2xl font-extrabold mb-1 tracking-tight">{prediction.possibleFinding}</h2>
              <p className="text-white/80 text-xs font-medium">Model Output: {prediction.predictedClass}</p>
            </div>
            
            <div className="p-6 space-y-4">
              <div>
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Confidence Score</p>
                <div className="flex items-end gap-3 mb-2">
                  <span className="text-3xl font-extrabold text-slate-800">{(prediction.confidence * 100).toFixed(2)}%</span>
                  <span className={`text-[11px] font-bold px-2.5 py-1 rounded-full ${
                    isHighConfidence ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                  }`}>
                    {prediction.confidenceLevel}
                  </span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div 
                    className={`h-2 rounded-full transition-all duration-700 ease-out ${isHighConfidence ? 'bg-emerald-500' : 'bg-amber-500'}`}
                    style={{ width: `${prediction.confidence * 100}%` }}
                  ></div>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 flex justify-between text-xs">
                <span className="text-slate-500 font-medium">Model Architecture</span>
                <span className="font-bold text-slate-800">{prediction.model || 'DenseNet121'}</span>
              </div>
              
              <div className="pt-3 border-t border-slate-100">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">Review Status</p>
                <p className="font-semibold text-amber-700 bg-amber-50 p-2.5 rounded-xl border border-amber-100 flex items-center gap-2 text-xs">
                  <Activity size={16} className="animate-pulse" />
                  {prediction.reviewStatus || 'Radiologist Review Required'}
                </p>
              </div>
            </div>
          </div>

          {/* Patient Details Card */}
          <div className="card p-6 stagger-2">
            <div className="flex justify-between items-center mb-4 border-b border-slate-100 pb-3">
              <h3 className="text-xs font-bold text-slate-800 flex items-center gap-2 tracking-wider">
                <User className="text-[var(--color-primary-purple)]" size={18} />
                PATIENT DETAILS
              </h3>
              {isEmergency ? (
                <span className="bg-red-100 text-red-700 text-[11px] font-bold px-2 py-0.5 rounded flex items-center gap-1">
                  <AlertTriangle size={12} /> EMERGENCY
                </span>
              ) : (
                <span className="bg-emerald-100 text-emerald-700 text-[11px] font-bold px-2 py-0.5 rounded flex items-center gap-1">
                  <ShieldCheck size={12} /> ROUTINE
                </span>
              )}
            </div>
            
            <div className="space-y-3 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-500">Patient ID</span>
                <span className="font-bold text-[var(--color-primary-purple)]">{patient.patientId}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Patient Name</span>
                <span className="font-semibold text-slate-800">{patient.patientName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Age / Gender</span>
                <span className="font-semibold text-slate-800">{patient.age} / <span className="capitalize">{patient.gender}</span></span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Scan Type</span>
                <span className="font-semibold text-slate-800">{scan.scanType}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Uploaded Date</span>
                <span className="font-semibold text-slate-800">{new Date(scan.uploadedAt).toLocaleDateString()}</span>
              </div>
            </div>
          </div>

        </div>
      </div>

      {/* Image Preview Modal */}
      {previewModalImg && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4 fade-in" onClick={() => setPreviewModalImg(null)}>
          <div className="relative max-w-4xl w-full max-h-[90vh] bg-slate-900 rounded-2xl p-2 border border-slate-800 overflow-hidden shadow-2xl flex flex-col items-center justify-center" onClick={e => e.stopPropagation()}>
            <button 
              onClick={() => setPreviewModalImg(null)}
              className="absolute top-4 right-4 p-2 bg-slate-800/80 text-white rounded-full hover:bg-slate-700 transition-colors z-10"
            >
              <X size={20} />
            </button>
            <img src={previewModalImg} alt="Enlarged Scan Preview" className="max-h-[85vh] max-w-full object-contain rounded-xl" />
          </div>
        </div>
      )}
    </div>
  );
};

export default Prediction;
