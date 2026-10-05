import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  LayoutDashboard, 
  Upload, 
  Users, 
  FileText, 
  BarChart2, 
  AlertTriangle,
  Bell,
  Settings,
  Activity,
  X
} from 'lucide-react';

const Sidebar = ({ isOpen, setSidebarOpen }) => {
  const { user } = useAuth();

  const menuItems = [
    { path: '/dashboard', icon: <LayoutDashboard size={20} />, label: 'Dashboard' },
    { path: '/upload', icon: <Upload size={20} />, label: 'Upload Scan' },
    { path: '/patients', icon: <Users size={20} />, label: 'Patients' },
    { path: '/reports', icon: <FileText size={20} />, label: 'Reports' },
    { path: '/analytics', icon: <BarChart2 size={20} />, label: 'Analytics' },
    { path: '/emergency', icon: <AlertTriangle size={20} />, label: 'Emergency Cases' },
  ];

  const otherItems = [
    { path: '/notifications', icon: <Bell size={20} />, label: 'Notifications' },
    { path: '/settings', icon: <Settings size={20} />, label: 'Settings' },
  ];

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-xs z-40 lg:hidden transition-opacity duration-300 animate-fade-in"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 h-full w-64 bg-[var(--color-sidebar-dark)] text-slate-300 z-50 transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 lg:static flex flex-col shadow-2xl lg:shadow-none select-none
      `}>
        {/* Logo/Brand */}
        <div className="flex items-center justify-between px-6 py-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <img src="/scanova-logo.png" alt="Scanova AI Logo" className="w-10 h-10 object-contain rounded-xl bg-white p-1" />
            <div>
              <h1 className="text-white font-bold text-lg tracking-wide leading-tight">SCANOVA AI</h1>
              <p className="text-[10px] font-medium text-slate-400 uppercase tracking-widest">Radiology Assistant</p>
            </div>
          </div>
          <button 
            onClick={() => setSidebarOpen(false)} 
            className="lg:hidden text-slate-400 hover:text-white p-1 rounded-lg transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Menu Navigation */}
        <div className="flex-1 overflow-y-auto py-6 px-4 space-y-8">
          
          <nav className="space-y-1.5">
            <h3 className="px-4 text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-2">
              Main Menu
            </h3>
            {menuItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) => `
                  flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200 group relative
                  ${isActive 
                    ? 'bg-gradient-to-r from-[var(--color-primary-purple)] to-[#5b3ce4] text-white shadow-md shadow-purple-900/20' 
                    : 'hover:bg-white/5 hover:text-white hover:translate-x-0.5'
                  }
                `}
              >
                {({ isActive }) => (
                  <>
                    <span className={`transition-transform duration-200 ${isActive ? 'scale-110 text-white' : 'group-hover:scale-105'}`}>
                      {item.icon}
                    </span>
                    <span className="flex-1">{item.label}</span>
                    {isActive && (
                      <span className="w-1.5 h-4 bg-white/80 rounded-full animate-fade-in" />
                    )}
                  </>
                )}
              </NavLink>
            ))}
          </nav>

          <div className="space-y-1.5">
            <h3 className="px-4 text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-2">
              Management
            </h3>
            {otherItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) => `
                  flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200 group relative
                  ${isActive 
                    ? 'bg-gradient-to-r from-[var(--color-primary-purple)] to-[#5b3ce4] text-white shadow-md shadow-purple-900/20' 
                    : 'hover:bg-white/5 hover:text-white hover:translate-x-0.5'
                  }
                `}
              >
                {({ isActive }) => (
                  <>
                    <span className={`transition-transform duration-200 ${isActive ? 'scale-110 text-white' : 'group-hover:scale-105'}`}>
                      {item.icon}
                    </span>
                    <span className="flex-1">{item.label}</span>
                    {isActive && (
                      <span className="w-1.5 h-4 bg-white/80 rounded-full animate-fade-in" />
                    )}
                  </>
                )}
              </NavLink>
            ))}
          </div>
        </div>

        {/* Doctor Profile (Bottom) */}
        {user && (
          <div className="p-4 border-t border-white/10 bg-[var(--color-sidebar-light)]/80 backdrop-blur-xs">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-500 flex items-center justify-center text-white font-bold text-sm flex-shrink-0 shadow-sm">
                {user.fullName ? user.fullName.charAt(0).toUpperCase() : 'D'}
              </div>
              <div className="overflow-hidden flex-1">
                <p className="text-white text-sm font-semibold truncate leading-tight">{user.fullName}</p>
                <p className="text-xs text-slate-400 truncate mt-0.5">{user.specialization || 'Radiology Department'}</p>
              </div>
            </div>
          </div>
        )}
      </aside>
    </>
  );
};

export default Sidebar;
