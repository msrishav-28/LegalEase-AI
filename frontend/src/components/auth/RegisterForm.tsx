'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { FileText, Eye, EyeOff, CheckCircle, X, Loader2, AlertCircle } from 'lucide-react';
import { registerSchema, RegisterFormData, validatePassword } from '@/lib/validation';
import { useAuthStore } from '@/lib/stores/auth';
import { cn } from '@/lib/utils';

interface RegisterFormProps {
  redirectTo?: string;
  className?: string;
}

export default function RegisterForm({ redirectTo = '/dashboard', className }: RegisterFormProps) {
  const router = useRouter();
  const { register: registerUser, isLoading, error, clearError } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
      organization: '',
      agreeToTerms: false,
    },
  });

  const password = watch('password');
  const passwordValidation = password ? validatePassword(password) : null;

  const onSubmit = async (data: RegisterFormData) => {
    clearError();
    
    const { confirmPassword, agreeToTerms, ...userData } = data;
    
    const result = await registerUser(userData);
    
    if (result.success) {
      router.push(redirectTo);
    } else {
      setError('root', {
        message: result.error || 'Registration failed',
      });
    }
  };

  const displayError = errors.root?.message || error;

  return (
    <div className={cn('w-full max-w-md mx-auto', className)}>
      <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        <div className="sm:mx-auto sm:w-full sm:max-w-md mb-8">
          <div className="flex justify-center">
            <div className="flex items-center space-x-2">
              <FileText className="h-8 w-8 text-primary-600" />
              <span className="text-2xl font-bold text-gray-900">LegalEase AI</span>
            </div>
          </div>
          <h2 className="mt-6 text-center text-3xl font-bold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Already have an account?{' '}
            <Link href="/login" className="font-medium text-primary-600 hover:text-primary-500">
              Sign in
            </Link>
          </p>
        </div>

        {displayError && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <div className="flex items-center">
              <AlertCircle className="h-4 w-4 text-red-500 mr-2" />
              <span className="text-sm text-red-700">{displayError}</span>
            </div>
          </div>
        )}

        <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">
              Full name
            </label>
            <div className="mt-1">
              <input
                {...register('name')}
                id="name"
                type="text"
                autoComplete="name"
                className={cn(
                  'appearance-none block w-full px-3 py-2 border rounded-md placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                  errors.name
                    ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                    : 'border-gray-300'
                )}
                placeholder="Enter your full name"
              />
              {errors.name && (
                <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
              )}
            </div>
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              Email address
            </label>
            <div className="mt-1">
              <input
                {...register('email')}
                id="email"
                type="email"
                autoComplete="email"
                className={cn(
                  'appearance-none block w-full px-3 py-2 border rounded-md placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                  errors.email
                    ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                    : 'border-gray-300'
                )}
                placeholder="Enter your email"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
              )}
            </div>
          </div>

          <div>
            <label htmlFor="organization" className="block text-sm font-medium text-gray-700">
              Organization (optional)
            </label>
            <div className="mt-1">
              <input
                {...register('organization')}
                id="organization"
                type="text"
                className={cn(
                  'appearance-none block w-full px-3 py-2 border rounded-md placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                  errors.organization
                    ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                    : 'border-gray-300'
                )}
                placeholder="Enter your organization"
              />
              {errors.organization && (
                <p className="mt-1 text-sm text-red-600">{errors.organization.message}</p>
              )}
            </div>
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <div className="mt-1 relative">
              <input
                {...register('password')}
                id="password"
                type={showPassword ? 'text' : 'password'}
                autoComplete="new-password"
                className={cn(
                  'appearance-none block w-full px-3 py-2 pr-10 border rounded-md placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                  errors.password
                    ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                    : 'border-gray-300'
                )}
                placeholder="Create a password"
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4 text-gray-400" />
                ) : (
                  <Eye className="h-4 w-4 text-gray-400" />
                )}
              </button>
            </div>
            
            {/* Password validation indicators */}
            {password && passwordValidation && (
              <div className="mt-2 space-y-1">
                <div className="flex items-center text-xs">
                  {passwordValidation.checks.length ? (
                    <CheckCircle className="w-3 h-3 text-green-500 mr-1" />
                  ) : (
                    <X className="w-3 h-3 text-red-500 mr-1" />
                  )}
                  <span className={passwordValidation.checks.length ? 'text-green-600' : 'text-red-600'}>
                    At least 8 characters
                  </span>
                </div>
                <div className="flex items-center text-xs">
                  {passwordValidation.checks.uppercase ? (
                    <CheckCircle className="w-3 h-3 text-green-500 mr-1" />
                  ) : (
                    <X className="w-3 h-3 text-red-500 mr-1" />
                  )}
                  <span className={passwordValidation.checks.uppercase ? 'text-green-600' : 'text-red-600'}>
                    One uppercase letter
                  </span>
                </div>
                <div className="flex items-center text-xs">
                  {passwordValidation.checks.lowercase ? (
                    <CheckCircle className="w-3 h-3 text-green-500 mr-1" />
                  ) : (
                    <X className="w-3 h-3 text-red-500 mr-1" />
                  )}
                  <span className={passwordValidation.checks.lowercase ? 'text-green-600' : 'text-red-600'}>
                    One lowercase letter
                  </span>
                </div>
                <div className="flex items-center text-xs">
                  {passwordValidation.checks.number ? (
                    <CheckCircle className="w-3 h-3 text-green-500 mr-1" />
                  ) : (
                    <X className="w-3 h-3 text-red-500 mr-1" />
                  )}
                  <span className={passwordValidation.checks.number ? 'text-green-600' : 'text-red-600'}>
                    One number
                  </span>
                </div>
                <div className="flex items-center text-xs">
                  {passwordValidation.checks.special ? (
                    <CheckCircle className="w-3 h-3 text-green-500 mr-1" />
                  ) : (
                    <X className="w-3 h-3 text-red-500 mr-1" />
                  )}
                  <span className={passwordValidation.checks.special ? 'text-green-600' : 'text-red-600'}>
                    One special character
                  </span>
                </div>
              </div>
            )}
            
            {errors.password && (
              <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
              Confirm password
            </label>
            <div className="mt-1 relative">
              <input
                {...register('confirmPassword')}
                id="confirmPassword"
                type={showConfirmPassword ? 'text' : 'password'}
                autoComplete="new-password"
                className={cn(
                  'appearance-none block w-full px-3 py-2 pr-10 border rounded-md placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
                  errors.confirmPassword
                    ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                    : 'border-gray-300'
                )}
                placeholder="Confirm your password"
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              >
                {showConfirmPassword ? (
                  <EyeOff className="h-4 w-4 text-gray-400" />
                ) : (
                  <Eye className="h-4 w-4 text-gray-400" />
                )}
              </button>
            </div>
            {errors.confirmPassword && (
              <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>
            )}
          </div>

          <div className="flex items-start">
            <input
              {...register('agreeToTerms')}
              id="agreeToTerms"
              type="checkbox"
              className={cn(
                'h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded mt-0.5',
                errors.agreeToTerms ? 'border-red-300' : ''
              )}
            />
            <label htmlFor="agreeToTerms" className="ml-2 block text-sm text-gray-900">
              I agree to the{' '}
              <Link href="/terms" className="text-primary-600 hover:text-primary-500">
                Terms of Service
              </Link>{' '}
              and{' '}
              <Link href="/privacy" className="text-primary-600 hover:text-primary-500">
                Privacy Policy
              </Link>
            </label>
          </div>
          {errors.agreeToTerms && (
            <p className="text-sm text-red-600">{errors.agreeToTerms.message}</p>
          )}

          <div>
            <button
              type="submit"
              disabled={isSubmitting || isLoading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {isSubmitting || isLoading ? (
                <>
                  <Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4" />
                  Creating account...
                </>
              ) : (
                'Create account'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}