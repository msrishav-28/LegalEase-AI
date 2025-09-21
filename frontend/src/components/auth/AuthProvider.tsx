'use client';

import { useEffect, ReactNode } from 'react';
import { useAuthStore } from '@/lib/stores/auth';

interface AuthProviderProps {
  children: ReactNode;
}

export default function AuthProvider({ children }: AuthProviderProps) {
  const { initializeAuth } = useAuthStore();

  useEffect(() => {
    // Initialize authentication state when the app loads
    initializeAuth();
  }, [initializeAuth]);

  return <>{children}</>;
}