import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        surface: '#f7faf8',
        card: '#ffffff',
        ink: '#11223a',
        accent: '#0d9488',
        accent2: '#f97316',
      },
      keyframes: {
        rise: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        }
      },
      animation: {
        rise: 'rise 350ms ease-out',
      }
    },
  },
  plugins: [],
}

export default config
