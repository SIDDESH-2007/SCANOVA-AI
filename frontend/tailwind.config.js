export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sidebar: {
          dark: '#07152B',
          light: '#0B1D3A'
        },
        primary: {
          purple: '#6C4CF5',
          blue: '#3B82F6'
        },
        accent: {
          mri: '#F472B6',
          ct: '#4ADE80',
          xray: '#60A5FA'
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUpSm: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleInSm: {
          '0%': { opacity: '0', transform: 'scale(0.98)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.25s ease-out forwards',
        'slide-up-sm': 'slideUpSm 0.25s ease-out forwards',
        'scale-in-sm': 'scaleInSm 0.2s ease-out forwards',
      }
    },
  },
  plugins: [],
}
