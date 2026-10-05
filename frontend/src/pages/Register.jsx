import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Activity, User, Mail, Building, Stethoscope, Phone, Lock } from 'lucide-react';
import ToastContainer from '../components/ToastContainer';
import { toast } from '../utils/toast';

const Register = () => {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    hospital: '',
    department: '',
    specialization: '',
    phone: '',
    password: '',
    confirmPassword: ''
  });
  
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({...formData, [e.target.name]: e.target.value});
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (submitting) return;
    
    if (Object.values(formData).some(val => !val)) {
      setError('Please fill in all fields');
      toast.error('Please fill in all fields');
      return;
    }
    
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      toast.error('Passwords do not match');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      await register(formData);
      toast.success('Account created successfully! Please sign in.');
      navigate('/login');
    } catch (err) {
      const msg = err.message || 'Registration failed';
      setError(msg);
      toast.error(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--color-bg-light)] py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl w-full bg-white rounded-3xl shadow-xl p-8 sm:p-10 border border-slate-100 animate-slide-up-sm">
        
        <div className="flex flex-col items-center mb-8 text-center">
          <div className="bg-[var(--color-primary-purple)] p-2.5 rounded-2xl text-white mb-3 shadow-md shadow-purple-900/20">
            <Activity size={30} />
          </div>
          <h2 className="text-3xl font-bold text-slate-800 tracking-tight">Create Account</h2>
          <p className="text-slate-500 mt-1 text-sm">Join the AI-powered medical diagnostic platform.</p>
        </div>

        {error && (
          <div className="bg-rose-50 border border-rose-200 text-rose-600 p-3.5 rounded-xl mb-6 text-sm font-medium text-center animate-fade-in">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            {/* Full Name */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Full Name</label>
              <div className="relative">
                <User className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  type="text"
                  name="fullName"
                  value={formData.fullName}
                  onChange={handleChange}
                  className="input-field pl-10"
                  placeholder="Dr. John Doe"
                  required
                />
              </div>
            </div>

            {/* Email Address */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="input-field pl-10"
                  placeholder="doctor@hospital.com"
                  required
                />
              </div>
            </div>

            {/* Hospital */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Hospital / Organization</label>
              <div className="relative">
                <Building className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  type="text"
                  name="hospital"
                  value={formData.hospital}
                  onChange={handleChange}
                  className="input-field pl-10"
                  placeholder="Central City Hospital"
                  required
                />
              </div>
            </div>

            {/* Department */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Department</label>
              <div className="relative">
                <Building className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  type="text"
                  name="department"
                  value={formData.department}
                  onChange={handleChange}
                  className="input-field pl-10"
                  placeholder="Radiology"
                  required
                />
              </div>
            </div>

            {/* Specialization */}
            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Specialization</label>
              <div className="relative">
                <Stethoscope className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  type="text"
                  name="specialization"
                  value={formData.specialization}
                  onChange={handleChange}
                  className="input-field pl-10"
                  placeholder="Neuro-radiologist"
                  required
                />
              </div>
            </div>

            {/* Phone */}
            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Phone Number</label>
              <div className="relative">
                <Phone className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  className="input-field pl-10"
                  placeholder="+91 9876543210"
                  required
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Password</label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="input-field pl-10"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Confirm Password</label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className="input-field pl-10"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>
            
          </div>

          <div className="pt-4">
            <button type="submit" disabled={submitting} className="w-full btn-primary py-3 text-base font-semibold shadow-md">
              {submitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Creating Account...</span>
                </>
              ) : (
                'Create Account'
              )}
            </button>
          </div>
        </form>

        <p className="mt-6 text-center text-sm text-slate-600 border-t border-slate-100 pt-4">
          Already have an account?{' '}
          <Link to="/login" className="font-semibold text-[var(--color-primary-purple)] hover:underline">
            Sign In
          </Link>
        </p>

      </div>
      <ToastContainer />
    </div>
  );
};

export default Register;
