import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'LangGraph Multi-Agent System',
  description: 'AI-powered multi-agent system with business, research, and technical expertise',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
