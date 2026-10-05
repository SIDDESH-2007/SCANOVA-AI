import React, { useState, useEffect } from 'react';
import PageHeader from '../components/PageHeader';
import { Bell, CheckCircle2, Activity, AlertCircle, FileText } from 'lucide-react';
import api from '../services/api';
import { Link } from 'react-router-dom';
import EmptyState from '../components/EmptyState';
import toast from '../utils/toast';

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchNotifications = async () => {
    try {
      const res = await api.get('/notifications');
      setNotifications(res.data);
    } catch (err) {
      console.error(err);
      toast.error('Failed to load notifications');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const markAsRead = async (id) => {
    try {
      await api.put(`/notifications/${id}/read`);
      setNotifications(prev => prev.map(n => n.notificationId === id ? { ...n, isRead: true } : n));
      toast.success('Notification marked as read');
    } catch (err) {
      console.error(err);
      toast.error('Failed to update notification');
    }
  };

  const markAllAsRead = async () => {
    try {
      await api.put('/notifications/read-all');
      setNotifications(prev => prev.map(n => ({ ...n, isRead: true })));
      toast.success('All notifications marked as read');
    } catch (err) {
      console.error(err);
      toast.error('Failed to update notifications');
    }
  };

  const getIcon = (type) => {
    switch(type) {
      case 'EMERGENCY': return <AlertCircle className="text-red-500 flex-shrink-0" size={20} />;
      case 'REPORT': return <FileText className="text-blue-500 flex-shrink-0" size={20} />;
      default: return <Activity className="text-[var(--color-primary-purple)] flex-shrink-0" size={20} />;
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 fade-in">
      <PageHeader 
        title="Notification Center"
        subtitle="View all real-time system alerts, DICOM analysis events, and priority notifications."
        action={
          notifications.some(n => !n.isRead) && (
            <button onClick={markAllAsRead} className="btn-secondary text-xs flex items-center gap-1.5 py-2 px-3">
              <CheckCircle2 size={16} />
              Mark all as read
            </button>
          )
        }
      />

      <div className="card overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-100 flex items-center justify-between">
          <h3 className="font-bold text-slate-800 text-base">Recent Notifications</h3>
          <span className="text-xs font-bold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-full">
            {notifications.filter(n => !n.isRead).length} Unread
          </span>
        </div>
        
        {loading ? (
          <div className="p-16 text-center text-slate-400 flex flex-col items-center">
            <div className="w-8 h-8 border-4 border-slate-200 border-t-[var(--color-primary-purple)] rounded-full animate-spin mb-3"></div>
            <p className="text-sm font-medium">Loading notifications...</p>
          </div>
        ) : notifications.length === 0 ? (
          <EmptyState 
            icon={Bell}
            title="No notifications yet"
            description="When a scan is uploaded, analyzed, or a report is generated, real-time alerts will appear here."
          />
        ) : (
          <div className="divide-y divide-slate-100">
            {notifications.map(n => (
              <div 
                key={n.notificationId} 
                className={`p-4 sm:p-6 transition-all duration-300 flex gap-4 ${
                  !n.isRead ? 'bg-purple-50/40 border-l-4 border-l-[var(--color-primary-purple)]' : 'hover:bg-slate-50'
                }`}
              >
                <div className="mt-0.5">
                  {getIcon(n.type)}
                </div>
                <div className="flex-1">
                  <div className="flex justify-between items-start mb-1">
                    <h4 className={`text-sm ${!n.isRead ? 'font-bold text-slate-900' : 'font-semibold text-slate-700'}`}>
                      {n.title}
                    </h4>
                    <span className="text-[11px] font-medium text-slate-400 whitespace-nowrap ml-4">
                      {new Date(n.createdAt).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 mb-3 leading-relaxed">{n.message}</p>
                  
                  <div className="flex items-center gap-4">
                    {n.link && (
                      <Link to={n.link} className="text-xs font-bold text-[var(--color-primary-purple)] hover:underline flex items-center gap-1">
                        View Details →
                      </Link>
                    )}
                    {!n.isRead && (
                      <button onClick={() => markAsRead(n.notificationId)} className="text-xs font-semibold text-slate-400 hover:text-slate-700 transition-colors">
                        Mark as read
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Notifications;
