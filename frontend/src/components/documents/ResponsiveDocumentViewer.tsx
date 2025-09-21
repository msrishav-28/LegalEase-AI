'use client';

import React, { useState, useCallback, useEffect } from 'react';
import { DocumentViewer } from './DocumentViewer';
import { AnnotationToolbar, AnnotationType } from './AnnotationToolbar';
import { Document as DocumentType } from '../../types';
import { useMediaQuery } from '../../hooks/useMediaQuery';

interface ResponsiveDocumentViewerProps {
  document: DocumentType;
  documentUrl: string;
  onTextSelect?: (selectedText: string, pageNumber: number) => void;
  onAnnotationCreate?: (annotation: any) => void;
  onAnnotationUpdate?: (annotationId: string, updates: any) => void;
  onAnnotationDelete?: (annotationId: string) => void;
  annotations?: any[];
  className?: string;
}

interface PendingAnnotation {
  type: AnnotationType;
  pageNumber: number;
  x: number;
  y: number;
  width?: number;
  height?: number;
  text?: string;
  comment?: string;
}

export const ResponsiveDocumentViewer: React.FC<ResponsiveDocumentViewerProps> = ({
  document,
  documentUrl,
  onTextSelect,
  onAnnotationCreate,
  onAnnotationUpdate,
  onAnnotationDelete,
  annotations = [],
  className = ''
}) => {
  const [selectedTool, setSelectedTool] = useState<AnnotationType | null>(null);
  const [pendingAnnotation, setPendingAnnotation] = useState<PendingAnnotation | null>(null);
  const [selectedAnnotation, setSelectedAnnotation] = useState<string | null>(null);
  const [showAnnotationDialog, setShowAnnotationDialog] = useState(false);
  const [annotationComment, setAnnotationComment] = useState('');

  // Responsive breakpoints
  const isMobile = useMediaQuery('(max-width: 768px)');
  const isTablet = useMediaQuery('(max-width: 1024px)');

  // Handle text selection for highlighting
  const handleTextSelect = useCallback((selectedText: string, pageNumber: number) => {
    if (selectedTool === 'highlight') {
      const selection = window.getSelection();
      if (selection && selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        
        const annotation: PendingAnnotation = {
          type: 'highlight',
          pageNumber,
          x: rect.left,
          y: rect.top,
          width: rect.width,
          height: rect.height,
          text: selectedText
        };
        
        setPendingAnnotation(annotation);
        setShowAnnotationDialog(true);
      }
    }
    
    onTextSelect?.(selectedText, pageNumber);
  }, [selectedTool, onTextSelect]);

  // Handle annotation creation
  const handleCreateAnnotation = useCallback(() => {
    if (pendingAnnotation) {
      const newAnnotation = {
        id: `annotation-${Date.now()}`,
        ...pendingAnnotation,
        comment: annotationComment,
        userId: 'current-user', // This should come from auth context
        userName: 'Current User', // This should come from auth context
        createdAt: new Date().toISOString()
      };
      
      onAnnotationCreate?.(newAnnotation);
      setPendingAnnotation(null);
      setAnnotationComment('');
      setShowAnnotationDialog(false);
      setSelectedTool(null);
    }
  }, [pendingAnnotation, annotationComment, onAnnotationCreate]);

  // Handle annotation deletion
  const handleDeleteAnnotation = useCallback(() => {
    if (selectedAnnotation) {
      onAnnotationDelete?.(selectedAnnotation);
      setSelectedAnnotation(null);
    }
  }, [selectedAnnotation, onAnnotationDelete]);

  // Cancel pending annotation
  const handleCancelAnnotation = useCallback(() => {
    setPendingAnnotation(null);
    setAnnotationComment('');
    setShowAnnotationDialog(false);
  }, []);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setSelectedTool(null);
        handleCancelAnnotation();
      }
      
      if (event.key === 'Delete' && selectedAnnotation) {
        handleDeleteAnnotation();
      }
      
      if ((event.ctrlKey || event.metaKey) && event.key === 's' && pendingAnnotation) {
        event.preventDefault();
        handleCreateAnnotation();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [selectedAnnotation, pendingAnnotation, handleDeleteAnnotation, handleCreateAnnotation, handleCancelAnnotation]);

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Annotation Toolbar - responsive positioning */}
      <div className={`
        ${isMobile ? 'order-2 mt-2' : 'order-1 mb-4'}
        flex justify-center
      `}>
        <AnnotationToolbar
          selectedTool={selectedTool}
          onToolSelect={setSelectedTool}
          onSaveAnnotation={handleCreateAnnotation}
          onDeleteAnnotation={handleDeleteAnnotation}
          hasActiveAnnotation={!!pendingAnnotation || !!selectedAnnotation}
          className={isMobile ? 'w-full' : ''}
        />
      </div>

      {/* Document Viewer */}
      <div className={`
        ${isMobile ? 'order-1' : 'order-2'}
        flex-1 min-h-0
      `}>
        <DocumentViewer
          documentUrl={documentUrl}
          documentName={document.name}
          onTextSelect={handleTextSelect}
          onAnnotationCreate={onAnnotationCreate}
          annotations={annotations}
          className="h-full"
        />
      </div>

      {/* Annotation Dialog */}
      {showAnnotationDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className={`
            bg-white rounded-lg shadow-xl
            ${isMobile ? 'w-full max-w-sm' : 'w-full max-w-md'}
          `}>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">
                Add {pendingAnnotation?.type === 'highlight' ? 'Highlight' : 'Annotation'}
              </h3>
              
              {pendingAnnotation?.text && (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Selected Text:
                  </label>
                  <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md text-sm">
                    "{pendingAnnotation.text}"
                  </div>
                </div>
              )}
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Comment (optional):
                </label>
                <textarea
                  value={annotationComment}
                  onChange={(e) => setAnnotationComment(e.target.value)}
                  placeholder="Add your comment here..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                  rows={3}
                />
              </div>
              
              <div className="flex justify-end space-x-3">
                <button
                  onClick={handleCancelAnnotation}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors duration-200"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateAnnotation}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors duration-200"
                >
                  Save
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Mobile-specific styles */}
      <style jsx>{`
        @media (max-width: 768px) {
          .react-pdf__Page__canvas {
            max-width: 100% !important;
            height: auto !important;
          }
        }
      `}</style>
    </div>
  );
};

export default ResponsiveDocumentViewer;