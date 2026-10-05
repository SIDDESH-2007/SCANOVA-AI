import React, { useState, useEffect } from 'react';
import { Menu, Search, Bell, LogOut, User as UserIcon } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import api from '../services/api';
import { toast } from '../utils/toast';

const Topbar = ({ setSidebarOpen }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const fetchUnreadNotifications = async () => {
      try {
        const res = await api.get('/notifications');
        const count = res.data.filter(n => !n.isRead).length;
        setUnreadCount(count);
      } catch (err) {
        // silent
      }
    };
    fetchUnreadNotifications();
    const interval = setInterval(fetchUnreadNotifications, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleLogout = () => {
    logout();
    toast.info('Signed out successfully.');
    navigate('/login');
  };

  return (
    <header className="bg-white border-b border-slate-200/80 h-16 flex items-center justify-between px-4 lg:px-8 z-30 sticky top-0 shadow-xs">
      
      {/* Left section */}
      <div className="flex items-center gap-4 flex-1">
        <button 
          onClick={() => setSidebarOpen(true)}
          className="p-2 rounded-xl text-slate-600 hover:bg-slate-100 lg:hidden transition-colors"
          aria-label="Toggle Sidebar"
        >
          <Menu size={22} />
        </button>
        
        <div className="hidden md:flex items-center relative w-full max-w-md group">
          <Search className="absolute left-3.5 text-slate-400 group-focus-within:text-[var(--color-primary-purple)] transition-colors" size={18} />
          <input 
            type="text" 
            placeholder="Search patients, scans, or reports..." 
            className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-purple)]/20 focus:border-[var(--color-primary-purple)] focus:bg-white transition-all duration-200"
          />
        </div>
      </div>

      {/* Right section */}
      <div className="flex items-center gap-3 sm:gap-4 ml-4">
        <Link 
          to="/notifications" 
          className="p-2 rounded-xl text-slate-600 hover:bg-slate-100 transition-all duration-200 relative group"
          title="Notifications"
        >
          <Bell size={20} className="group-hover:scale-105 transition-transform" />
          {unreadCount > 0 && (
            <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-rose-500 rounded-full border-2 border-white animate-pulse" />
          )}
        </Link>
        
        <div className="h-6 w-px bg-slate-200 mx-0.5"></div>
        
        <div className="flex items-center gap-3">
          <div className="hidden sm:block text-right">
            <p className="text-sm font-semibold text-slate-800 leading-snug">{user?.fullName || 'Doctor'}</p>
            <button 
              onClick={handleLogout} 
              className="text-xs font-medium text-slate-500 hover:text-rose-600 transition-colors flex items-center justify-end gap-1 ml-auto"
            >
              <span>Sign out</span>
              <LogOut size={12} />
            </button>
          </div>
          <div className="w-10 h-10 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-600 font-bold shadow-xs">
            <UserIcon size={20} />
          </div>
        </div>
      </div>
      
    </header>
  );
};

export default Topbar;
