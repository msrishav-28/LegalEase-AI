'use client';

import { useEffect, ReactNode } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { useAuthStore } from '@/lib/stores/auth';

interface ProtectedRouteProps {
  children: ReactNode;
  requiredRole?: 'admin' | 'user' | 'viewer';
  fallbackPath?: string;
  loadingComponent?: ReactNode;
}

export default function ProtectedRoute({
  children,
  requiredRole,
  fallbackPath = '/login',
  loadingComponent,
}: ProtectedRouteProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, isAuthenticated, initializeAuth } = useAuthStore();

  useEffect(() => {
    // Initialize auth state on mount
    initializeAuth();
  }, [initializeAuth]);

  useEffect(() => {
    if (!isAuthenticated) {
      // Redirect to login with return URL
      const returnUrl = encodeURIComponent(pathname);
      router.push(`${fallbackPath}?returnUrl=${returnUrl}`);
      return;
    }

    // Check role-based access
    if (requiredRole && user) {
      const roleHierarchy = {
        viewer: 0,
        user: 1,
        admin: 2,
      };

      const userRoleLevel = roleHierarchy[user.role];
      const requiredRoleLevel = roleHierarchy[requiredRole];

      if (userRoleLevel < requiredRoleLevel) {
        // User doesn't have sufficient permissions
        router.push('/unauthorized');
        return;
      }
    }
  }, [isAuthenticated, user, requiredRole, router, pathname, fallbackPath]);

  // Show loading state while checking authentication
  if (!isAuthenticated || (requiredRole && !user)) {
    return (
      loadingComponent || (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary-600 mx-auto" />
            <p className="mt-2 text-sm text-gray-600">Loading...</p>
          </div>
        </div>
      )
    );
  }

  return <>{children}</>;
}

// Higher-order component for easier usage
export function withAuth<P extends object>(
  Component: React.ComponentType<P>,
  options?: {
    requiredRole?: 'admin' | 'user' | 'viewer';
    fallbackPath?: string;
  }
) {
  return function AuthenticatedComponent(props: P) {
    return (
      <ProtectedRoute
        requiredRole={options?.requiredRole}
        fallbackPath={options?.fallbackPath}
      >
        <Component {...props} />
      </ProtectedRoute>
    );
  };
}