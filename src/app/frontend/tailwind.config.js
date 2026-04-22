/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#0e7490',
          light: '#22d3ee',
          dark: '#0c4a6e',
        },
        benign: { DEFAULT: '#0891b2', bg: '#ecfeff' },
        malignant: { DEFAULT: '#dc2626', bg: '#fef2f2' },
        normal: { DEFAULT: '#059669', bg: '#ecfdf5' },
      },
      fontFamily: {
        sans: [
          '-apple-system', 'BlinkMacSystemFont', 'Segoe UI',
          'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'sans-serif',
        ],
      },
    },
  },
  plugins: [],
}
