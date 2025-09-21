'use client';

import { useState } from 'react';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import UserProfile from '@/components/auth/UserProfile';
import ChangePasswordForm from '@/components/auth/ChangePasswordForm';
import { User, Lock } from 'lucide-react';
import { cn } from '@/lib/utils';

type TabType = 'profile' | 'security';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<TabType>('profile');

  const tabs = [
    {
      id: 'profile' as TabType,
      name: 'Profile',
      icon: User,
      description: 'Manage your account information',
    },
    {
      id: 'security' as TabType,
      name: 'Security',
      icon: Lock,
      description: 'Update your password and security settings',
    },
  ];

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
              <p className="mt-2 text-sm text-gray-600">
                Manage your account settings and preferences
              </p>
            </div>

            <div className="lg:grid lg:grid-cols-12 lg:gap-x-5">
              {/* Sidebar */}
              <aside className="py-6 px-2 sm:px-6 lg:py-0 lg:px-0 lg:col-span-3">
                <nav className="space-y-1">
                  {tabs.map((tab) => {
                    const Icon = tab.icon;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={cn(
                          'group rounded-md px-3 py-2 flex items-center text-sm font-medium w-full text-left',
                          activeTab === tab.id
                            ? 'bg-primary-50 text-primary-700 hover:text-primary-700 hover:bg-primary-50'
                            : 'text-gray-900 hover:text-gray-900 hover:bg-gray-50'
                        )}
                      >
                        <Icon
                          className={cn(
                            'flex-shrink-0 -ml-1 mr-3 h-6 w-6',
                            activeTab === tab.id
                              ? 'text-primary-500'
                              : 'text-gray-400 group-hover:text-gray-500'
                          )}
                        />
                        <span className="truncate">{tab.name}</span>
                      </button>
                    );
                  })}
                </nav>
              </aside>

              {/* Main content */}
              <div className="space-y-6 sm:px-6 lg:px-0 lg:col-span-9">
                {activeTab === 'profile' && (
                  <div>
                    <div className="mb-6">
                      <h2 className="text-lg font-medium text-gray-900">Profile Information</h2>
                      <p className="mt-1 text-sm text-gray-600">
                        Update your account details and personal information
                      </p>
                    </div>
                    <UserProfile />
                  </div>
                )}

                {activeTab === 'security' && (
                  <div>
                    <div className="mb-6">
                      <h2 className="text-lg font-medium text-gray-900">Security Settings</h2>
                      <p className="mt-1 text-sm text-gray-600">
                        Manage your password and account security
                      </p>
                    </div>
                    <ChangePasswordForm />
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}