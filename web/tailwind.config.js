/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#1A73E8',
        background: '#F8F9FA',
        surface: '#FFFFFF',
        'text-primary': '#1C1C1E',
        'text-secondary': '#6B6B6B',
      },
      borderRadius: {
        DEFAULT: '12px',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
