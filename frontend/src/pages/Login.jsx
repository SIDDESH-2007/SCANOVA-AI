import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Activity, Mail, Lock } from 'lucide-react';
import ToastContainer from '../components/ToastContainer';
import { toast } from '../utils/toast';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [step, setStep] = useState(1);
  const [otp, setOtp] = useState('');
  const [userId, setUserId] = useState(null);
  
  const [submitting, setSubmitting] = useState(false);
  
  const { login, verifyLogin2FA } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (submitting) return;

    if (step === 1) {
      if (!email.trim() || !password) {
        setError('Please fill in all fields');
        return;
      }
      setSubmitting(true);
      setError('');
      try {
        const res = await login(email.trim(), password);
        if (res.requiresTwoFactor) {
          setUserId(res.userId);
          setStep(2);
          toast.info('Two-factor authentication code required.');
        } else {
          toast.success('Signed in successfully!');
          navigate('/dashboard');
        }
      } catch (err) {
        const msg = err?.message || 'Invalid email or password';
        setError(msg);
        toast.error(msg);
      } finally {
        setSubmitting(false);
      }
    } else {
      if (!otp.trim()) {
        setError('Please enter the verification code');
        return;
      }
      setSubmitting(true);
      setError('');
      try {
        await verifyLogin2FA(userId, otp.trim());
        toast.success('Verification successful!');
        navigate('/dashboard');
      } catch (err) {
        const msg = err?.message || 'Invalid verification code';
        setError(msg);
        toast.error(msg);
      } finally {
        setSubmitting(false);
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--color-bg-light)] p-4 sm:p-6 lg:p-8">
      <div className="flex w-full max-w-5xl min-h-[580px] bg-white rounded-3xl shadow-xl border border-slate-100 overflow-hidden animate-slide-up-sm">
        
        {/* Left side - Login Form */}
        <div className="w-full lg:w-1/2 p-8 sm:p-12 flex flex-col justify-between relative">
          
          <div className="flex items-center gap-3 mb-6">
            <img src="/scanova-logo.png" alt="Scanova AI Logo" className="w-12 h-12 object-contain" />
            <div>
              <span className="font-bold text-[var(--color-sidebar-dark)] text-xl tracking-wide leading-none block">SCANOVA AI</span>
              <span className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-1 block">Hospital Portal</span>
            </div>
          </div>

          <div className="max-w-md w-full mx-auto my-auto py-4">
            <div className="mb-6">
              <h2 className="text-2xl sm:text-3xl font-bold text-slate-800 tracking-tight">Welcome Back</h2>
              <p className="text-slate-500 text-sm mt-1">Sign in to your hospital account to continue.</p>
            </div>

            {error && (
              <div className="bg-rose-50 border border-rose-200 text-rose-600 p-3.5 rounded-xl mb-6 text-sm font-medium flex items-center gap-2 animate-fade-in">
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {step === 1 ? (
                <>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Email Address</label>
                    <div className="relative">
                      <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                      <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="input-field pl-10"
                        placeholder="doctor@hospital.com"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Password</label>
                    <div className="relative">
                      <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                      <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="input-field pl-10"
                        placeholder="••••••••"
                        required
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-1">
                    <label className="flex items-center gap-2 cursor-pointer select-none">
                      <input type="checkbox" className="w-4 h-4 rounded text-[var(--color-primary-purple)] focus:ring-[var(--color-primary-purple)] border-slate-300 transition-colors" />
                      <span className="text-sm text-slate-600">Remember Me</span>
                    </label>
                    <a href="#" className="text-sm font-semibold text-[var(--color-primary-purple)] hover:underline">
                      Forgot Password?
                    </a>
                  </div>
                </>
              ) : (
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Two-Factor Authentication Code</label>
                  <div className="relative">
                    <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                    <input
                      type="text"
                      value={otp}
                      onChange={(e) => setOtp(e.target.value)}
                      className="input-field pl-10 tracking-widest text-lg font-mono"
                      placeholder="123456"
                      maxLength={6}
                    />
                  </div>
                  <p className="text-xs text-slate-500 mt-2">Enter the 6-digit code from your authenticator app.</p>
                </div>
              )}

              <button
                type="submit"
                disabled={submitting}
                className="w-full btn-primary py-3 mt-4 text-base font-semibold shadow-md"
              >
                {submitting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>{step === 1 ? 'Signing In...' : 'Verifying...'}</span>
                  </>
                ) : (
                  step === 1 ? 'Sign In' : 'Verify Code'
                )}
              </button>
            </form>
          </div>

          {step === 1 && (
            <p className="text-center text-sm text-slate-600 pt-4 border-t border-slate-100 mt-4">
              Don't have an account?{' '}
              <Link to="/register" className="font-semibold text-[var(--color-primary-purple)] hover:underline">
                Create Account
              </Link>
            </p>
          )}
        </div>

        {/* Right side - Image/Pattern */}
        <div className="hidden lg:flex w-1/2 bg-[var(--color-sidebar-dark)] p-12 items-center justify-center relative overflow-hidden">
          {/* Decorative circles */}
          <div className="absolute top-[-10%] right-[-10%] w-96 h-96 bg-[var(--color-primary-purple)] rounded-full mix-blend-multiply filter blur-3xl opacity-25"></div>
          <div className="absolute bottom-[-10%] left-[-10%] w-96 h-96 bg-[var(--color-primary-blue)] rounded-full mix-blend-multiply filter blur-3xl opacity-25"></div>
          
          <div className="relative z-10 text-center text-white max-w-sm">
            <div className="mb-8 flex justify-center">
              <div className="w-48 h-48 rounded-full border-[16px] border-white/10 flex items-center justify-center relative shadow-2xl">
                <div className="w-32 h-32 rounded-full border-[8px] border-[var(--color-primary-purple)]/50 flex items-center justify-center">
                  <Activity size={48} className="text-[var(--color-primary-blue)] animate-pulse" />
                </div>
              </div>
            </div>
            <h3 className="text-2xl font-bold mb-4 leading-tight">Advanced AI for<br/>Medical Imaging</h3>
            <p className="text-slate-300 text-sm leading-relaxed">
              Enhance diagnostic accuracy with our state-of-the-art AI support system for X-ray, CT, and MRI scans.
            </p>
          </div>
        </div>

      </div>

      <ToastContainer />
    </div>
  );
};

export default Login;
