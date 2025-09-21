'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { ArrowLeft, AlertCircle } from 'lucide-react';
import { DocumentComparison } from '@/components/documents';
import { documentApi } from '@/lib/api';
import { Document } from '@/types';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

export default function DocumentComparePage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  
  const [document1, setDocument1] = useState<Document | null>(null);
  const [document2, setDocument2] = useState<Document | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const document1Id = searchParams.get('doc1');
  const document2Id = searchParams.get('doc2');
  const comparisonId = searchParams.get('comparison');

  // Load documents
  useEffect(() => {
    const loadDocuments = async () => {
      if (!document1Id || !document2Id) {
        setError('Both documents must be specified for comparison');
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null);

        const [doc1Response, doc2Response] = await Promise.all([
          documentApi.getDocument(document1Id),
          documentApi.getDocument(document2Id)
        ]);

        if (!doc1Response.success || !doc1Response.data) {
          throw new Error(doc1Response.error || 'Failed to load first document');
        }

        if (!doc2Response.success || !doc2Response.data) {
          throw new Error(doc2Response.error || 'Failed to load second document');
        }

        setDocument1(doc1Response.data);
        setDocument2(doc2Response.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load documents');
      } finally {
        setIsLoading(false);
      }
    };

    loadDocuments();
  }, [document1Id, document2Id]);

  // Handle back navigation
  const handleBack = () => {
    router.back();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <LoadingSpinner size="lg" />
            <p className="mt-4 text-gray-600">Loading documents for comparison...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="mb-8">
            <button
              onClick={handleBack}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-4"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back</span>
            </button>
            
            <h1 className="text-2xl font-bold text-gray-900">Document Comparison</h1>
          </div>

          {/* Error State */}
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-red-800 mb-2">
                Unable to Load Documents
              </h3>
              <p className="text-red-600 mb-4">{error}</p>
              <button
                onClick={() => router.push('/documents')}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Return to Documents
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!document1 || !document2) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Documents Not Found
              </h3>
              <p className="text-gray-600 mb-4">
                One or both documents could not be loaded for comparison.
              </p>
              <button
                onClick={() => router.push('/documents')}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Return to Documents
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-full mx-auto">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={handleBack}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back</span>
              </button>
              
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  Document Comparison
                </h1>
                <p className="text-sm text-gray-600">
                  Comparing {document1.name} with {document2.name}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Comparison Interface */}
        <div className="h-[calc(100vh-120px)]">
          <DocumentComparison
            document1={document1}
            document2={document2}
            comparisonId={comparisonId || undefined}
            onComparisonComplete={(comparison) => {
              // Update URL with comparison ID if not already present
              if (!comparisonId && comparison.id) {
                const newUrl = new URL(window.location.href);
                newUrl.searchParams.set('comparison', comparison.id);
                window.history.replaceState({}, '', newUrl.toString());
              }
            }}
            className="h-full"
          />
        </div>
      </div>
    </div>
  );
}