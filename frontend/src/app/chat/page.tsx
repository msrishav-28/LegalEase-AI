'use client';

import React from 'react';
import { ChatInterface } from '@/components/chat';
import { Document } from '@/types';

// Mock document for demonstration
const mockDocument: Document = {
  id: 'doc-1',
  name: 'Service Agreement - Tech Consulting.pdf',
  type: 'contract',
  uploadedBy: 'user-1',
  uploadedAt: new Date().toISOString(),
  analysisStatus: 'completed',
  metadata: {
    fileSize: 2048576,
    pageCount: 12,
    parties: ['TechCorp Solutions Pvt Ltd', 'Global Innovations Inc'],
    jurisdiction: 'cross_border',
    documentDate: '2024-01-15',
    extractionMethod: 'text'
  },
  analysisResults: {
    id: 'analysis-1',
    documentId: 'doc-1',
    summary: {
      overview: 'Cross-border technology consulting agreement between Indian and US entities',
      keyPoints: [
        'Service delivery across multiple jurisdictions',
        'Intellectual property ownership clauses',
        'Payment terms in USD with Indian tax implications'
      ],
      recommendations: [
        'Review stamp duty requirements in India',
        'Clarify tax withholding obligations',
        'Add dispute resolution mechanism'
      ]
    },
    risks: [
      {
        id: 'risk-1',
        type: 'high',
        category: 'Compliance',
        description: 'Stamp duty non-compliance in India',
        impact: 'Agreement may be inadmissible in Indian courts',
        mitigation: 'Pay applicable stamp duty in the state of execution'
      }
    ],
    obligations: [
      {
        id: 'obl-1',
        party: 'TechCorp Solutions Pvt Ltd',
        description: 'Deliver consulting services within 90 days',
        dueDate: '2024-04-15',
        status: 'pending'
      }
    ],
    complexity: {
      overall: 7.5,
      legal: 8.0,
      financial: 7.0,
      operational: 7.5,
      explanation: 'High complexity due to cross-border nature and multiple regulatory frameworks'
    },
    keyTerms: [
      {
        term: 'Intellectual Property',
        definition: 'All work product created during the engagement',
        importance: 'high'
      }
    ],
    createdAt: new Date().toISOString()
  }
};

export default function ChatPage() {
  const handleDocumentReferenceClick = (reference: any) => {
    console.log('Document reference clicked:', reference);
    // In a real app, this would navigate to the document viewer
    // and highlight the referenced section
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Legal Document Chat
          </h1>
          <p className="text-gray-600">
            Ask questions about your legal documents with jurisdiction-aware AI assistance.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Document Info Panel */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Current Document
              </h2>
              
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-1">
                    Document Name
                  </h3>
                  <p className="text-sm text-gray-900">{mockDocument.name}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-1">
                    Type
                  </h3>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {mockDocument.type}
                  </span>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-1">
                    Jurisdiction
                  </h3>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                    Cross-Border (India/USA)
                  </span>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-1">
                    Parties
                  </h3>
                  <ul className="text-sm text-gray-900 space-y-1">
                    {mockDocument.metadata.parties.map((party, index) => (
                      <li key={index}>• {party}</li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-1">
                    Analysis Status
                  </h3>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Completed
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Chat Interface */}
          <div className="lg:col-span-2">
            <ChatInterface
              document={mockDocument}
              jurisdiction={mockDocument.metadata.jurisdiction}
              onDocumentReferenceClick={handleDocumentReferenceClick}
              className="h-[600px]"
            />
          </div>
        </div>

        {/* Usage Tips */}
        <div className="mt-8 bg-blue-50 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-blue-900 mb-4">
            💡 Chat Tips
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h3 className="text-sm font-medium text-blue-800 mb-2">
                Jurisdiction-Specific Questions
              </h3>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• "What is the stamp duty requirement?"</li>
                <li>• "Check GST implications"</li>
                <li>• "Analyze UCC applicability"</li>
                <li>• "Review CCPA compliance"</li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-sm font-medium text-blue-800 mb-2">
                General Analysis
              </h3>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• "What are the key risks?"</li>
                <li>• "Summarize main obligations"</li>
                <li>• "Find termination clauses"</li>
                <li>• "Compare enforceability"</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}