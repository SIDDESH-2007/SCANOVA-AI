import React, { useState, useEffect } from 'react';
import PageHeader from '../components/PageHeader';
import { useAuth } from '../context/AuthContext';
import { User, Shield, Sliders, Bell, Check, Lock } from 'lucide-react';
import api from '../services/api';
import toast from '../utils/toast';

const Settings = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  // Profile State
  const [profileData, setProfileData] = useState({
    fullName: user?.fullName || '',
    hospital: user?.hospital || '',
    department: user?.department || '',
    specialization: user?.specialization || '',
    phone: user?.phone || ''
  });

  // 2FA State
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(user?.twoFactorEnabled || false);
  const [showQr, setShowQr] = useState(false);
  const [qrUri, setQrUri] = useState('');
  const [token, setToken] = useState('');
  const [disablePassword, setDisablePassword] = useState('');

  // Preferences State
  const [preferences, setPreferences] = useState(user?.preferences || {
    dashboard: { showRecentScans: true, showScanDistribution: true, showEmergencySummary: true, showPendingReviews: true },
    dateFormat: 'DD/MM/YYYY',
    notifications: { systemNotifications: true, emergencyAlerts: true, reportAlerts: true, pendingReviewAlerts: true }
  });

  const handleProfileUpdate = async () => {
    setLoading(true);
    setSavedSuccess(false);
    try {
      await api.put('/settings/profile', profileData);
      setSavedSuccess(true);
      toast.success('Profile updated successfully');
      setTimeout(() => setSavedSuccess(false), 2500);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handlePreferencesUpdate = async (newPrefs) => {
    try {
      await api.put('/settings/preferences', newPrefs);
      setPreferences(newPrefs);
      toast.success('Preferences updated successfully');
    } catch (err) {
      toast.error('Failed to save preferences');
    }
  };

  const init2FA = async () => {
    try {
      const res = await api.post('/auth/2fa/setup');
      setQrUri(res.data.qrUri);
      setShowQr(true);
      toast.info('Scan the QR code with your authenticator app');
    } catch (err) {
      toast.error('Failed to initiate 2FA setup');
    }
  };

  const verify2FA = async () => {
    try {
      await api.post('/auth/2fa/verify-setup', { token });
      setTwoFactorEnabled(true);
      setShowQr(false);
      setToken('');
      toast.success('Two-Factor Authentication Enabled');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Invalid token');
    }
  };

  const disable2FA = async () => {
    if (!disablePassword) {
      toast.error('Password is required to disable 2FA');
      return;
    }
    try {
      await api.post('/auth/2fa/disable', { password: disablePassword });
      setTwoFactorEnabled(false);
      setDisablePassword('');
      toast.success('Two-Factor Authentication Disabled');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to disable 2FA');
    }
  };

  const tabs = [
    { id: 'profile', label: 'Profile', icon: <User size={18} /> },
    { id: 'account', label: 'Account', icon: <Lock size={18} /> },
    { id: 'security', label: 'Security', icon: <Shield size={18} /> },
    { id: 'preferences', label: 'Preferences', icon: <Sliders size={18} /> },
    { id: 'notifications', label: 'Notifications', icon: <Bell size={18} /> },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-6 fade-in">
      <PageHeader 
        title="Settings"
        subtitle="Manage account configurations, security features, and dashboard preferences."
      />

      <div className="flex flex-col md:flex-row gap-6">
        
        {/* Left Navigation */}
        <div className="w-full md:w-64 flex-shrink-0">
          <div className="card p-2">
            <nav className="space-y-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-sm font-semibold rounded-xl transition-all duration-200 ${
                    activeTab === tab.id 
                      ? 'bg-purple-50 text-[var(--color-primary-purple)] shadow-sm' 
                      : 'text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  {tab.icon}
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 card p-6 sm:p-8">
          
          {activeTab === 'profile' && (
            <div className="space-y-6 fade-in">
              <h3 className="text-lg font-bold text-slate-800 border-b border-slate-100 pb-4">Profile Information</h3>
              
              <div className="flex items-center gap-6 mb-6">
                <div className="w-20 h-20 bg-gradient-to-br from-[var(--color-primary-purple)] to-purple-800 rounded-full flex items-center justify-center text-white text-2xl font-extrabold shadow-md">
                  {user?.fullName?.charAt(0) || 'D'}
                </div>
                <div>
                  <button className="btn-secondary text-xs mb-1.5 py-2 px-3">Change Avatar</button>
                  <p className="text-[11px] text-slate-400">JPG, GIF or PNG. Max size 2MB.</p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
                  <input type="text" className="input-field" value={profileData.fullName} onChange={e => setProfileData({...profileData, fullName: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
                  <input type="email" className="input-field bg-slate-50 text-slate-500 cursor-not-allowed" defaultValue={user?.email || ''} readOnly />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Hospital / Medical Center</label>
                  <input type="text" className="input-field" value={profileData.hospital} onChange={e => setProfileData({...profileData, hospital: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Department</label>
                  <input type="text" className="input-field" value={profileData.department} onChange={e => setProfileData({...profileData, department: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Specialization</label>
                  <input type="text" className="input-field" value={profileData.specialization} onChange={e => setProfileData({...profileData, specialization: e.target.value})} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Phone Number</label>
                  <input type="tel" className="input-field" value={profileData.phone} onChange={e => setProfileData({...profileData, phone: e.target.value})} placeholder="+1 (555) 000-0000" />
                </div>
              </div>

              <div className="pt-4 flex justify-end">
                <button onClick={handleProfileUpdate} disabled={loading} className="btn-primary min-w-[140px] flex items-center justify-center gap-2">
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>Saving...</span>
                    </>
                  ) : savedSuccess ? (
                    <>
                      <Check size={18} />
                      <span>Saved ✓</span>
                    </>
                  ) : (
                    <span>Save Changes</span>
                  )}
                </button>
              </div>
            </div>
          )}

          {activeTab === 'account' && (
            <div className="space-y-6 fade-in">
              <h3 className="text-lg font-bold text-slate-800 border-b border-slate-100 pb-4">Account Settings</h3>
              <div className="space-y-4 max-w-md">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Current Email</label>
                  <input type="email" className="input-field bg-slate-50 text-slate-500 cursor-not-allowed" defaultValue={user?.email || ''} readOnly />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">New Email</label>
                  <input type="email" className="input-field" placeholder="Enter new email" />
                </div>
                <button className="btn-secondary text-xs py-2 px-4">Update Email</button>
              </div>
              
              <div className="space-y-4 max-w-md pt-6 border-t border-slate-100">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Current Password</label>
                  <input type="password" className="input-field" placeholder="••••••••" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">New Password</label>
                  <input type="password" className="input-field" placeholder="••••••••" />
                </div>
                <button className="btn-primary text-xs py-2.5 px-4">Update Password</button>
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="space-y-6 fade-in">
              <h3 className="text-lg font-bold text-slate-800 border-b border-slate-100 pb-4">Security</h3>
              
              <div className="flex flex-col p-5 border border-slate-200 rounded-xl gap-4 bg-slate-50/50">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-bold text-slate-800 text-sm">Two-Factor Authentication (2FA)</h4>
                    <p className="text-xs text-slate-500 mt-0.5">Add TOTP 6-digit authentication security to your account.</p>
                  </div>
                  {!twoFactorEnabled && !showQr && (
                    <button onClick={init2FA} className="btn-secondary text-xs py-2 px-4">Enable 2FA</button>
                  )}
                </div>

                {showQr && !twoFactorEnabled && (
                  <div className="mt-4 p-5 bg-white border border-slate-200 rounded-xl flex flex-col items-center shadow-sm fade-in">
                    <p className="text-xs font-bold text-slate-700 mb-4">1. Scan QR Code using Google Authenticator / Authy</p>
                    <div className="bg-white p-3 rounded-xl border border-slate-200 mb-4 shadow-sm">
                      <img src={`https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(qrUri)}`} alt="2FA QR Code" />
                    </div>
                    <p className="text-xs font-bold text-slate-700 mb-2">2. Enter 6-digit Verification Token</p>
                    <div className="flex gap-2">
                      <input 
                        type="text" 
                        maxLength={6} 
                        className="input-field w-36 text-center tracking-widest font-mono text-sm" 
                        value={token}
                        onChange={e => setToken(e.target.value)}
                        placeholder="000000"
                      />
                      <button onClick={verify2FA} className="btn-primary text-xs py-2 px-4">Verify Token</button>
                    </div>
                  </div>
                )}

                {twoFactorEnabled && (
                  <div className="mt-4 p-4 bg-red-50 border border-red-100 rounded-xl flex flex-col gap-3 fade-in">
                    <p className="text-xs font-bold text-red-700">Disable Two-Factor Authentication</p>
                    <div className="flex gap-2 max-w-sm">
                      <input 
                        type="password" 
                        className="input-field bg-white text-xs" 
                        value={disablePassword}
                        onChange={e => setDisablePassword(e.target.value)}
                        placeholder="Enter password to confirm"
                      />
                      <button onClick={disable2FA} className="btn-primary bg-red-600 hover:bg-red-700 text-xs whitespace-nowrap py-2 px-4">Disable</button>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="mt-8">
                <h4 className="font-bold text-slate-800 text-sm mb-4">Active Login Sessions</h4>
                <div className="p-4 border border-slate-200 rounded-xl flex items-center justify-between bg-white">
                  <div>
                    <p className="font-bold text-slate-800 text-xs">Windows 11 • Google Chrome</p>
                    <p className="text-[11px] text-slate-400">Current Session • Active Now</p>
                  </div>
                  <span className="text-[11px] font-bold bg-emerald-100 text-emerald-700 px-2.5 py-0.5 rounded-full">Active</span>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'preferences' && (
            <div className="space-y-6 fade-in">
              <h3 className="text-lg font-bold text-slate-800 border-b border-slate-100 pb-4">System Preferences</h3>
              
              <div className="space-y-6 max-w-md">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Date Display Format</label>
                  <select 
                    className="input-field bg-white text-xs"
                    value={preferences.dateFormat}
                    onChange={e => handlePreferencesUpdate({ ...preferences, dateFormat: e.target.value })}
                  >
                    <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                    <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                    <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                  </select>
                </div>

                <div className="pt-4 border-t border-slate-100">
                  <h4 className="font-bold text-slate-800 text-sm mb-3">Dashboard Displays</h4>
                  {[
                    { key: 'showRecentScans', label: 'Show Recent Medical Scans' },
                    { key: 'showScanDistribution', label: 'Show Modality Breakdown' },
                    { key: 'showEmergencySummary', label: 'Show Emergency Priority Bar' },
                    { key: 'showPendingReviews', label: 'Show Pending Clinical Reviews' }
                  ].map(item => (
                    <div key={item.key} className="flex items-center justify-between py-2.5 border-b border-slate-50">
                      <span className="text-xs text-slate-700 font-medium">{item.label}</span>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input 
                          type="checkbox" 
                          className="sr-only peer" 
                          checked={preferences.dashboard[item.key]} 
                          onChange={e => handlePreferencesUpdate({
                            ...preferences,
                            dashboard: { ...preferences.dashboard, [item.key]: e.target.checked }
                          })}
                        />
                        <div className="w-10 h-5 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all duration-200 peer-checked:bg-[var(--color-primary-purple)]"></div>
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="space-y-6 fade-in">
              <h3 className="text-lg font-bold text-slate-800 border-b border-slate-100 pb-4">Notification Preferences</h3>
              
              <div className="space-y-4">
                {[
                  { key: 'emergencyAlerts', title: 'Critical / Emergency Alerts', desc: 'Instant notifications when high-priority DICOM scans are analyzed.' },
                  { key: 'reportAlerts', title: 'Report Notifications', desc: 'Receive updates when new diagnostic reports are generated.' },
                  { key: 'pendingReviewAlerts', title: 'Pending Clinical Reviews', desc: 'Receive alerts for scans awaiting radiologist sign-off.' },
                  { key: 'systemNotifications', title: 'Browser Push Notifications', desc: 'Enable native desktop system notifications for real-time alerts.' }
                ].map((item, idx) => (
                  <div key={idx} className="flex items-start justify-between p-4 border border-slate-100 rounded-xl bg-slate-50/50">
                    <div>
                      <h4 className="font-bold text-slate-800 text-xs mb-0.5">{item.title}</h4>
                      <p className="text-[11px] text-slate-500">{item.desc}</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer mt-0.5">
                      <input 
                        type="checkbox" 
                        className="sr-only peer" 
                        checked={preferences.notifications[item.key]} 
                        onChange={e => {
                          const val = e.target.checked;
                          if (item.key === 'systemNotifications' && val) {
                            if ('Notification' in window) {
                              Notification.requestPermission().then(permission => {
                                if (permission === 'granted') {
                                  handlePreferencesUpdate({
                                    ...preferences,
                                    notifications: { ...preferences.notifications, systemNotifications: true }
                                  });
                                } else {
                                  toast.error('Browser notification permission denied');
                                }
                              });
                            }
                          } else {
                            handlePreferencesUpdate({
                              ...preferences,
                              notifications: { ...preferences.notifications, [item.key]: val }
                            });
                          }
                        }}
                      />
                      <div className="w-10 h-5 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all duration-200 peer-checked:bg-[var(--color-primary-purple)]"></div>
                    </label>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default Settings;
