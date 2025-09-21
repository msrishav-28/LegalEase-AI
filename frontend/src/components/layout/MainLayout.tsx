'use client';

import { ReactNode } from 'react';
import Header from './Header';
import Footer from './Footer';
import Sidebar from './Sidebar';

interface MainLayoutProps {
  children: ReactNode;
  showSidebar?: boolean;
  user?: {
    name: string;
    email: string;
  } | null;
}

export default function MainLayout({ 
  children, 
  showSidebar = true, 
  user 
}: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header user={user} />
      
      <div className="flex-1 flex">
        {showSidebar && (
          <div className="hidden lg:flex lg:flex-shrink-0">
            <Sidebar />
          </div>
        )}
        
        <main className="flex-1 overflow-hidden">
          <div className="h-full">
            {children}
          </div>
        </main>
      </div>
      
      <Footer />
    </div>
  );
}