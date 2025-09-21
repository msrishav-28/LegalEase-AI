'use client';

import React, { useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Upload } from 'lucide-react';
import { DocumentList, DocumentUploadModal } from '@/components/documents';
import { Document } from '@/types';

export default function DocumentsPage() {
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [documents, setDocuments] = useState<Document[]>([
    {
      id: '1',
      name: 'Service Agreement - TechCorp.pdf',
      type: 'contract',
      content: '',
      metadata: {
        fileSize: 2516582, // 2.4 MB in bytes
        pageCount: 15,
        parties: ['TechCorp Inc.', 'Client Solutions Ltd.'],
        jurisdiction: 'india',
        documentDate: '2024-01-10',
        extractionMethod: 'text',
      },
      uploadedBy: 'user1',
      uploadedAt: '2024-01-15T10:30:00Z',
      analysisStatus: 'completed',
      analysisResults: {
        id: 'analysis1',
        documentId: '1',
        summary: {
          overview: 'Service agreement between TechCorp and Client Solutions',
          keyPoints: ['Payment terms', 'Service scope', 'Termination clauses'],
          recommendations: ['Review payment schedule', 'Clarify IP ownership'],
        },
        risks: [],
        obligations: [],
        complexity: {
          overall: 85,
          legal: 80,
          financial: 90,
          operational: 85,
          explanation: 'Moderately complex agreement with standard terms',
        },
        keyTerms: [],
        createdAt: '2024-01-15T10:35:00Z',
      },
    },
    {
      id: '2',
      name: 'NDA - StartupXYZ.pdf',
      type: 'nda',
      content: '',
      metadata: {
        fileSize: 1887437, // 1.8 MB in bytes
        pageCount: 8,
        parties: ['StartupXYZ Inc.', 'Consulting Partners LLC'],
        jurisdiction: 'usa',
        documentDate: '2024-01-12',
        extractionMethod: 'text',
      },
      uploadedBy: 'user1',
      uploadedAt: '2024-01-15T09:15:00Z',
      analysisStatus: 'processing',
    },
    {
      id: '3',
      name: 'Partnership MOU.pdf',
      type: 'mou',
      content: '',
      metadata: {
        fileSize: 3355443, // 3.2 MB in bytes
        pageCount: 22,
        parties: ['Global Corp', 'International Partners', 'Local Subsidiary'],
        jurisdiction: 'cross_border',
        documentDate: '2024-01-08',
        extractionMethod: 'ocr',
      },
      uploadedBy: 'user1',
      uploadedAt: '2024-01-14T16:45:00Z',
      analysisStatus: 'completed',
      analysisResults: {
        id: 'analysis3',
        documentId: '3',
        summary: {
          overview: 'Cross-border partnership memorandum',
          keyPoints: ['Multi-jurisdiction compliance', 'Revenue sharing', 'Governance structure'],
          recommendations: ['Legal review in all jurisdictions', 'Tax implications assessment'],
        },
        risks: [],
        obligations: [],
        complexity: {
          overall: 92,
          legal: 95,
          financial: 88,
          operational: 93,
          explanation: 'Highly complex cross-border agreement',
        },
        keyTerms: [],
        createdAt: '2024-01-14T17:00:00Z',
      },
    },
    {
      id: '4',
      name: 'Employment Contract.pdf',
      type: 'contract',
      content: '',
      metadata: {
        fileSize: 1572864, // 1.5 MB in bytes
        pageCount: 12,
        parties: ['ABC Company', 'John Doe'],
        jurisdiction: 'india',
        documentDate: '2024-01-05',
        extractionMethod: 'text',
      },
      uploadedBy: 'user1',
      uploadedAt: '2024-01-14T14:20:00Z',
      analysisStatus: 'failed',
    },
  ]);

  const handleUploadSuccess = (uploadedFiles: any[]) => {
    // Convert uploaded files to Document format and add to list
    const newDocuments: Document[] = uploadedFiles.map(file => ({
      id: file.id,
      name: file.name,
      type: file.type,
      content: '',
      metadata: {
        fileSize: file.size,
        pageCount: 0, // Will be determined during processing
        parties: [],
        jurisdiction: file.jurisdiction,
        extractionMethod: 'text',
      },
      uploadedBy: 'current-user', // In real app, get from auth context
      uploadedAt: file.uploadedAt,
      analysisStatus: 'pending',
    }));

    setDocuments(prev => [...newDocuments, ...prev]);
  };

  const handleDocumentSelect = (document: Document) => {
    console.log('Selected document:', document);
    // In real app, navigate to document viewer
  };

  const handleDocumentDelete = (documentId: string) => {
    if (confirm('Are you sure you want to delete this document?')) {
      setDocuments(prev => prev.filter(doc => doc.id !== documentId));
    }
  };

  const handleDocumentDownload = (documentId: string) => {
    console.log('Download document:', documentId);
    // In real app, trigger download
  };

  const handleRefresh = () => {
    console.log('Refreshing documents...');
    // In real app, refetch from API
  };

  return (
    <MainLayout>
      <div className="p-6">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
            <p className="text-gray-600">Manage and analyze your legal documents</p>
          </div>
          <button 
            onClick={() => setIsUploadModalOpen(true)}
            className="btn-primary flex items-center"
          >
            <Upload className="w-4 h-4 mr-2" />
            Upload Document
          </button>
        </div>

        <DocumentList
          documents={documents}
          onDocumentSelect={handleDocumentSelect}
          onDocumentDelete={handleDocumentDelete}
          onDocumentDownload={handleDocumentDownload}
          onRefresh={handleRefresh}
        />

        <DocumentUploadModal
          isOpen={isUploadModalOpen}
          onClose={() => setIsUploadModalOpen(false)}
          onUploadSuccess={handleUploadSuccess}
        />
      </div>
    </MainLayout>
  );
}