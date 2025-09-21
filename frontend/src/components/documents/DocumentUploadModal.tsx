'use client';

import React, { useState } from 'react';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { DocumentType, Jurisdiction } from '@/types';
import DocumentUpload from './DocumentUpload';

interface DocumentUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadSuccess?: (uploadedFiles: any[]) => void;
}

export default function DocumentUploadModal({
  isOpen,
  onClose,
  onUploadSuccess,
}: DocumentUploadModalProps) {
  const [documentType, setDocumentType] = useState<DocumentType>('contract');
  const [jurisdiction, setJurisdiction] = useState<Jurisdiction>('india');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleUploadComplete = async (files: any[]) => {
    setIsSubmitting(true);
    
    try {
      // Here you would typically send the files to your API
      // For now, we'll simulate the process
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const uploadedFiles = files.map(file => ({
        id: file.id,
        name: file.name,
        type: documentType,
        jurisdiction,
        description,
        size: file.size,
        uploadedAt: new Date().toISOString(),
        status: 'processing',
      }));

      onUploadSuccess?.(uploadedFiles);
      onClose();
      
      // Reset form
      setDocumentType('contract');
      setJurisdiction('india');
      setDescription('');
    } catch (error) {
      console.error('Upload submission failed:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Backdrop */}
        <div
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          onClick={onClose}
        />

        {/* Modal */}
        <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">
              Upload Documents
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Document Metadata Form */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Document Type</label>
                <select
                  value={documentType}
                  onChange={(e) => setDocumentType(e.target.value as DocumentType)}
                  className="input-field"
                >
                  <option value="contract">Contract</option>
                  <option value="agreement">Agreement</option>
                  <option value="mou">MOU</option>
                  <option value="nda">NDA</option>
                  <option value="invoice">Invoice</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label className="label">Jurisdiction</label>
                <select
                  value={jurisdiction}
                  onChange={(e) => setJurisdiction(e.target.value as Jurisdiction)}
                  className="input-field"
                >
                  <option value="india">India</option>
                  <option value="usa">USA</option>
                  <option value="cross_border">Cross-border</option>
                  <option value="unknown">Unknown</option>
                </select>
              </div>
            </div>

            <div>
              <label className="label">Description (Optional)</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Brief description of the document..."
                rows={3}
                className="input-field resize-none"
              />
            </div>

            {/* File Upload Component */}
            <DocumentUpload
              onUploadComplete={handleUploadComplete}
              onUploadProgress={(fileId, progress) => {
                console.log(`File ${fileId}: ${progress}%`);
              }}
              onUploadError={(fileId, error) => {
                console.error(`File ${fileId} error:`, error);
              }}
            />

            {/* Upload Guidelines */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="text-sm font-medium text-blue-900 mb-2">
                Upload Guidelines
              </h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Supported formats: PDF, DOC, DOCX, TXT</li>
                <li>• Maximum file size: 50MB per file</li>
                <li>• Maximum 10 files per upload</li>
                <li>• Files will be automatically analyzed for jurisdiction and content</li>
                <li>• Processing may take a few minutes for large documents</li>
              </ul>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200">
            <button
              onClick={onClose}
              className="btn-outline"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              onClick={() => {
                // This would trigger the upload if files are selected
                // The actual upload is handled by the DocumentUpload component
              }}
              className={cn(
                'btn-primary',
                isSubmitting && 'opacity-50 cursor-not-allowed'
              )}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Processing...' : 'Upload & Analyze'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}