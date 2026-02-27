import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Goal Management System',
  description: 'Production-ready Goal Management System MVP',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
