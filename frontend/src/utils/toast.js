import eventBus from './eventBus';

export const toast = {
  success: (message, title = 'Success') => {
    eventBus.emit('show-toast', { type: 'success', title, message });
  },
  error: (message, title = 'Error') => {
    eventBus.emit('show-toast', { type: 'error', title, message });
  },
  warning: (message, title = 'Warning') => {
    eventBus.emit('show-toast', { type: 'warning', title, message });
  },
  info: (message, title = 'Info') => {
    eventBus.emit('show-toast', { type: 'info', title, message });
  }
};

export default toast;
