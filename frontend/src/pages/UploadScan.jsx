import React, { useState } from 'react';
import PageHeader from '../components/PageHeader';
import { Upload, X, File, FileImage, Image as ImageIcon, Activity, AlertTriangle, ShieldCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { sendSystemNotification } from '../utils/notifications';
import eventBus from '../utils/eventBus';
import toast from '../utils/toast';

const UploadScan = () => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [scanType, setScanType] = useState('X-RAY');
  const [caseType, setCaseType] = useState('normal');
  const [patientData, setPatientData] = useState({ name: '', age: '', gender: 'male', patientId: '', phoneNumber: '' });
  
  const MODALITIES = [
    { value: 'X-RAY', label: 'X-Ray', icon: FileImage },
    { value: 'CT', label: 'CT Scan', icon: File },
    { value: 'MRI', label: 'MRI Scan', icon: ImageIcon },
  ];
  
  const navigate = useNavigate();

  const handleFileSelect = (selectedFile) => {
    if (selectedFile) {
      setFile(selectedFile);
      if (selectedFile.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = () => setPreview(reader.result);
        reader.readAsDataURL(selectedFile);
      } else {
        setPreview(null);
      }
    }
  };

  const handleFileChange = (e) => {
    handleFileSelect(e.target.files[0]);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setPreview(null);
  };

  const [isUploading, setIsUploading] = useState(false);
  const [analysisStepIndex, setAnalysisStepIndex] = useState(0);
  const [error, setError] = useState('');

  const STEPS = [
    { label: "Validating scan image", desc: "Checking file dimensions & DICOM headers" },
    { label: "Checking image quality", desc: "Verifying contrast and blur metrics" },
    { label: "Selecting AI model", desc: "Loading DenseNet121 radiology weights" },
    { label: "Preprocessing scan", desc: "Normalizing intensity & resizing tensors" },
    { label: "Running neural analysis", desc: "Extracting deep feature maps" },
    { label: "Generating explainability", desc: "Computing Grad-CAM activation heatmaps" },
    { label: "Calculating confidence", desc: "Evaluating statistical certainty" },
    { label: "Preparing diagnostic report", desc: "Formatting clinical findings" }
  ];
  
  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!file) return;
    
    setIsUploading(true);
    setError('');
    setAnalysisStepIndex(0);

    let currentStep = 0;
    const stepInterval = setInterval(() => {
      currentStep++;
      if (currentStep < STEPS.length) {
        setAnalysisStepIndex(currentStep);
      }
    }, 550);

    const formData = new FormData();
    if (patientData.patientId) {
      formData.append('patientId', patientData.patientId);
    }
    formData.append('patientName', patientData.name);
    if (patientData.phoneNumber) {
      formData.append('phoneNumber', patientData.phoneNumber);
    }
    formData.append('age', patientData.age);
    formData.append('gender', patientData.gender);
    formData.append('scanType', scanType);
    formData.append('caseType', caseType);
    formData.append('file', file);

    try {
      const startTime = Date.now();
      
      const response = await api.post('/predictions/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      const elapsedTime = Date.now() - startTime;
      const minWait = 4400; // Polish animation (~4.4s)
      if (elapsedTime < minWait) {
        await new Promise(resolve => setTimeout(resolve, minWait - elapsedTime));
      }

      clearInterval(stepInterval);
      const result = response.data;
      
      const title = result.scan.caseType === 'EMERGENCY' ? 'Emergency Scan Requires Review' : 'Analysis Completed';
      const body = result.scan.caseType === 'EMERGENCY' 
        ? `Patient ${result.patient.patientId} has an emergency ${result.scan.scanType} analysis awaiting radiologist review.` 
        : `${result.scan.scanType} analysis completed for patient ${result.patient.patientId}.`;
        
      sendSystemNotification(title, { body });
      eventBus.emit('refreshData');
      toast.success('Medical scan analyzed successfully');
      navigate(`/prediction/${result.analysis.predictionId}`);
    } catch (err) {
      clearInterval(stepInterval);
      const msg = err.message || (typeof err === 'string' ? err : 'Analysis failed. Please try again.');
      setError(msg);
      toast.error(msg);
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <PageHeader 
        title="Upload Medical Scan"
        subtitle="Upload X-Ray, CT, or MRI scan for AI-powered clinical support analysis."
      />

      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden relative">
        
        {/* Analyzing Overlay */}
        {isUploading && (
          <div className="absolute inset-0 bg-white/98 z-50 flex flex-col items-center justify-center p-6 backdrop-blur-md fade-in">
            <div className="relative mb-6">
              <div className="w-20 h-20 border-4 border-slate-100 border-t-[var(--color-primary-purple)] rounded-full animate-spin"></div>
              <Activity className="absolute inset-0 m-auto text-[var(--color-primary-purple)] animate-pulse" size={28} />
            </div>

            <h2 className="text-2xl font-bold text-slate-800 mb-1">Analyzing Medical Scan</h2>
            <p className="text-sm font-semibold text-[var(--color-primary-purple)] mb-6 transition-all duration-300">
              {STEPS[analysisStepIndex].label}
            </p>

            {/* Progress bar */}
            <div className="w-full max-w-md bg-slate-100 h-2 rounded-full overflow-hidden mb-6">
              <div 
                className="bg-[var(--color-primary-purple)] h-full transition-all duration-500 ease-out"
                style={{ width: `${((analysisStepIndex + 1) / STEPS.length) * 100}%` }}
              ></div>
            </div>

            {/* Steps Checklist */}
            <div className="w-full max-w-md bg-slate-50 rounded-xl p-4 border border-slate-100 space-y-2">
              {STEPS.map((s, idx) => {
                const isDone = idx < analysisStepIndex;
                const isCurrent = idx === analysisStepIndex;
                return (
                  <div key={idx} className="flex items-center gap-3 text-xs">
                    <div className={`w-4 h-4 rounded-full flex items-center justify-center font-bold text-[10px] ${
                      isDone ? 'bg-emerald-500 text-white' : isCurrent ? 'bg-[var(--color-primary-purple)] text-white animate-pulse' : 'bg-slate-200 text-slate-400'
                    }`}>
                      {isDone ? '✓' : idx + 1}
                    </div>
                    <span className={`font-medium ${isCurrent ? 'text-slate-800 font-bold' : isDone ? 'text-slate-600 line-through opacity-70' : 'text-slate-400'}`}>
                      {s.label}
                    </span>
                  </div>
                );
              })}
            </div>
            
            <p className="text-xs text-slate-400 mt-4 text-center">
              Please do not refresh or navigate away while model predictions are being calculated.
            </p>
          </div>
        )}

        <form onSubmit={handleAnalyze} className="p-6 sm:p-8 space-y-8">
          
          {/* Patient Info */}
          <div>
            <h3 className="text-lg font-bold text-slate-800 mb-4 border-b border-slate-100 pb-2">Patient Information</h3>
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-slate-700 mb-1">Patient Name <span className="text-red-500">*</span></label>
                <input type="text" className="input-field" placeholder="e.g. Arun Kumar" value={patientData.name} onChange={(e) => setPatientData({...patientData, name: e.target.value})} required />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-slate-700 mb-1">Patient ID <span className="text-red-500">*</span></label>
                <input type="text" className="input-field" placeholder="PAT-001" value={patientData.patientId} onChange={(e) => setPatientData({...patientData, patientId: e.target.value})} required />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-slate-700 mb-1">Phone Number <span className="text-red-500">*</span></label>
                <input type="text" className="input-field" placeholder="9876543210 or +919876543210" value={patientData.phoneNumber} onChange={(e) => setPatientData({...patientData, phoneNumber: e.target.value})} required />
              </div>
              <div className="sm:col-span-1">
                <label className="block text-sm font-medium text-slate-700 mb-1">Age</label>
                <input type="number" className="input-field" placeholder="45" value={patientData.age} onChange={(e) => setPatientData({...patientData, age: e.target.value})} required />
              </div>
              <div className="sm:col-span-1">
                <label className="block text-sm font-medium text-slate-700 mb-1">Gender</label>
                <select className="input-field bg-white" value={patientData.gender} onChange={(e) => setPatientData({...patientData, gender: e.target.value})} required>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
          </div>

          {/* Case Type */}
          <div>
            <h3 className="text-lg font-bold text-slate-800 mb-4 border-b border-slate-100 pb-2">Case Priority</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <label className={`flex gap-4 p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 ${caseType === 'normal' ? 'border-emerald-500 bg-emerald-50/50 shadow-sm' : 'border-slate-200 hover:border-slate-300'}`}>
                <input type="radio" name="caseType" value="normal" checked={caseType === 'normal'} onChange={(e) => setCaseType(e.target.value)} className="hidden" />
                <div className={`mt-0.5 ${caseType === 'normal' ? 'text-emerald-600' : 'text-slate-400'}`}><ShieldCheck size={24} /></div>
                <div>
                  <h4 className={`font-bold ${caseType === 'normal' ? 'text-emerald-700' : 'text-slate-700'}`}>ROUTINE / NORMAL</h4>
                  <p className="text-xs text-slate-500 mt-1">Standard clinical diagnostic analysis</p>
                </div>
              </label>
              
              <label className={`flex gap-4 p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 ${caseType === 'emergency' ? 'border-red-500 bg-red-50/50 shadow-sm' : 'border-slate-200 hover:border-slate-300'}`}>
                <input type="radio" name="caseType" value="emergency" checked={caseType === 'emergency'} onChange={(e) => setCaseType(e.target.value)} className="hidden" />
                <div className={`mt-0.5 ${caseType === 'emergency' ? 'text-red-600' : 'text-slate-400'}`}><AlertTriangle size={24} /></div>
                <div>
                  <h4 className={`font-bold ${caseType === 'emergency' ? 'text-red-700' : 'text-slate-700'}`}>EMERGENCY PATIENT</h4>
                  <p className="text-xs text-slate-500 mt-1">Priority analysis requiring urgent clinical review</p>
                </div>
              </label>
            </div>
          </div>

          {/* Scan Modality */}
          <div>
            <h3 className="text-lg font-bold text-slate-800 mb-4 border-b border-slate-100 pb-2">Scan Modality</h3>
            <div className="grid grid-cols-3 gap-4">
              {MODALITIES.map((item) => {
                const IconComponent = item.icon;
                const isSelected = scanType === item.value;
                return (
                  <label key={item.value} className={`flex flex-col items-center justify-center p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 ${isSelected ? 'border-[var(--color-primary-purple)] bg-purple-50/60 shadow-sm' : 'border-slate-200 hover:border-slate-300'}`}>
                    <input type="radio" name="scanType" value={item.value} checked={isSelected} onChange={(e) => setScanType(e.target.value)} className="hidden" />
                    <IconComponent size={28} className={isSelected ? 'text-[var(--color-primary-purple)]' : 'text-slate-400'} />
                    <span className={`mt-2 font-medium text-sm ${isSelected ? 'text-[var(--color-primary-purple)] font-bold' : 'text-slate-600'}`}>
                      {item.label}
                    </span>
                  </label>
                );
              })}
            </div>
          </div>

          {/* Drag & Drop Upload Area */}
          <div>
            <h3 className="text-lg font-bold text-slate-800 mb-4 border-b border-slate-100 pb-2">Upload Image File</h3>
            
            {!file ? (
              <div 
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center text-center transition-all duration-200 cursor-pointer relative ${
                  isDragging 
                    ? 'border-[var(--color-primary-purple)] bg-purple-50/70 scale-[1.01]' 
                    : 'border-slate-300 hover:border-slate-400 bg-slate-50/50 hover:bg-slate-50'
                }`}
              >
                <input 
                  type="file" 
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" 
                  onChange={handleFileChange}
                  accept=".jpg,.jpeg,.png"
                />
                <div className="bg-white p-4 rounded-full shadow-sm mb-4 border border-slate-100">
                  <Upload size={32} className="text-[var(--color-primary-purple)]" />
                </div>
                <h4 className="text-base font-bold text-slate-700 mb-1">Drag & Drop or Browse Medical Scan</h4>
                <p className="text-slate-500 text-xs">Supported formats: JPG, JPEG, PNG</p>
                <p className="text-slate-400 text-xs mt-2">Max file size: 50MB</p>
              </div>
            ) : (
              <div className="border border-slate-200 rounded-xl p-4 flex flex-col sm:flex-row items-center gap-6 bg-slate-50/60 transition-all duration-200">
                <div className="w-full sm:w-44 h-44 bg-slate-900 rounded-xl overflow-hidden flex items-center justify-center flex-shrink-0 border border-slate-200 shadow-inner">
                  {preview ? (
                    <img src={preview} alt="Scan preview" className="w-full h-full object-contain" />
                  ) : (
                    <File size={48} className="text-slate-400" />
                  )}
                </div>
                <div className="flex-1 w-full">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-bold text-slate-800 truncate max-w-xs text-base">{file.name}</h4>
                      <p className="text-xs text-slate-500">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                      <div className="flex gap-2 mt-3">
                        <span className="text-[11px] bg-purple-100 text-[var(--color-primary-purple)] px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wide">{scanType}</span>
                        <span className={`text-[11px] px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wide ${caseType === 'emergency' ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'}`}>{caseType}</span>
                      </div>
                    </div>
                    <button type="button" onClick={handleRemoveFile} className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                      <X size={20} />
                    </button>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-2 mt-4 mb-1 overflow-hidden">
                    <div className="bg-[var(--color-primary-purple)] h-2 rounded-full w-full"></div>
                  </div>
                  <p className="text-[11px] text-slate-500 text-right font-medium">Ready for analysis</p>
                </div>
              </div>
            )}
          </div>

          {error && (
            <div className="bg-red-50 text-red-600 p-4 rounded-xl border border-red-100 flex items-start gap-3 fade-in text-sm">
              <X size={20} className="mt-0.5 flex-shrink-0" />
              <div>
                <h4 className="font-bold">Analysis Failed</h4>
                <p>{error}</p>
              </div>
            </div>
          )}

          <div className="pt-4 flex justify-end">
            <button 
              type="submit" 
              className={`btn-primary py-3 px-8 text-sm flex items-center gap-2 ${(!file || isUploading) ? 'opacity-50 cursor-not-allowed pointer-events-none' : ''}`} 
              disabled={!file || isUploading}
            >
              {isUploading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Analyzing Scan...</span>
                </>
              ) : (
                <>
                  <Activity size={18} />
                  <span>Analyze Scan</span>
                </>
              )}
            </button>
          </div>
          
        </form>
      </div>
    </div>
  );
};

export default UploadScan;
