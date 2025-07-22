import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import ClientLayout from './ClientLayout';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'BonMot - AI-Powered Writing Assistant',
  description: 'BonMot: Professional writing assistant with real-time grammar checking, spelling correction, and style suggestions',
  keywords: 'BonMot, grammar checker, spelling correction, writing assistant, AI writing, text editor',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.className} h-full bg-gray-50 antialiased`}>
        <ClientLayout>
          <div className="min-h-full">
            {children}
          </div>
        </ClientLayout>
      </body>
    </html>
  );
}
