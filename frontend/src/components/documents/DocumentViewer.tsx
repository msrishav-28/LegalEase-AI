'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { 
  ZoomIn, 
  ZoomOut, 
  ChevronLeft, 
  ChevronRight, 
  RotateCw,
  Download,
  Search,
  Maximize2,
  Minimize2
} from 'lucide-react';
import LoadingSpinner from '../ui/LoadingSpinner';

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

interface DocumentViewerProps {
  documentUrl: string;
  documentName: string;
  onTextSelect?: (selectedText: string, pageNumber: number) => void;
  onAnnotationCreate?: (annotation: Annotation) => void;
  annotations?: Annotation[];
  className?: string;
}

interface Annotation {
  id: string;
  pageNumber: number;
  x: number;
  y: number;
  width: number;
  height: number;
  text: string;
  comment?: string;
  userId: string;
  userName: string;
  createdAt: string;
}

interface TextSelection {
  text: string;
  pageNumber: number;
  boundingRect: DOMRect;
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({
  documentUrl,
  documentName,
  onTextSelect,
  onAnnotationCreate,
  annotations = [],
  className = ''
}) => {
  const [numPages, setNumPages] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [scale, setScale] = useState<number>(1.0);
  const [rotation, setRotation] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedText, setSelectedText] = useState<TextSelection | null>(null);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const pageRefs = useRef<{ [key: number]: HTMLDivElement }>({});

  // Handle document load success
  const onDocumentLoadSuccess = useCallback(({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
    setIsLoading(false);
    setError(null);
  }, []);

  // Handle document load error
  const onDocumentLoadError = useCallback((error: Error) => {
    setError(`Failed to load document: ${error.message}`);
    setIsLoading(false);
  }, []);

  // Navigation functions
  const goToPreviousPage = useCallback(() => {
    setCurrentPage(prev => Math.max(1, prev - 1));
  }, []);

  const goToNextPage = useCallback(() => {
    setCurrentPage(prev => Math.min(numPages, prev + 1));
  }, [numPages]);

  const goToPage = useCallback((page: number) => {
    if (page >= 1 && page <= numPages) {
      setCurrentPage(page);
    }
  }, [numPages]);

  // Zoom functions
  const zoomIn = useCallback(() => {
    setScale(prev => Math.min(3.0, prev + 0.25));
  }, []);

  const zoomOut = useCallback(() => {
    setScale(prev => Math.max(0.5, prev - 0.25));
  }, []);

  const resetZoom = useCallback(() => {
    setScale(1.0);
  }, []);

  // Rotation function
  const rotateDocument = useCallback(() => {
    setRotation(prev => (prev + 90) % 360);
  }, []);

  // Fullscreen toggle
  const toggleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  }, []);

  // Handle fullscreen change
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  // Handle text selection
  const handleTextSelection = useCallback(() => {
    const selection = window.getSelection();
    if (selection && selection.toString().trim()) {
      const range = selection.getRangeAt(0);
      const rect = range.getBoundingClientRect();
      
      const textSelection: TextSelection = {
        text: selection.toString(),
        pageNumber: currentPage,
        boundingRect: rect
      };
      
      setSelectedText(textSelection);
      onTextSelect?.(selection.toString(), currentPage);
    }
  }, [currentPage, onTextSelect]);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.ctrlKey || event.metaKey) {
        switch (event.key) {
          case '=':
          case '+':
            event.preventDefault();
            zoomIn();
            break;
          case '-':
            event.preventDefault();
            zoomOut();
            break;
          case '0':
            event.preventDefault();
            resetZoom();
            break;
          case 'f':
            event.preventDefault();
            toggleFullscreen();
            break;
        }
      } else {
        switch (event.key) {
          case 'ArrowLeft':
            event.preventDefault();
            goToPreviousPage();
            break;
          case 'ArrowRight':
            event.preventDefault();
            goToNextPage();
            break;
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [zoomIn, zoomOut, resetZoom, toggleFullscreen, goToPreviousPage, goToNextPage]);

  // Download function
  const downloadDocument = useCallback(() => {
    const link = document.createElement('a');
    link.href = documentUrl;
    link.download = documentName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }, [documentUrl, documentName]);

  if (error) {
    return (
      <div className={`flex items-center justify-center h-96 bg-gray-50 rounded-lg ${className}`}>
        <div className="text-center">
          <div className="text-red-500 text-lg font-medium mb-2">Error Loading Document</div>
          <div className="text-gray-600">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div 
      ref={containerRef}
      className={`flex flex-col bg-white border border-gray-200 rounded-lg overflow-hidden ${className}`}
    >
      {/* Toolbar */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center space-x-2">
          {/* Navigation */}
          <button
            onClick={goToPreviousPage}
            disabled={currentPage <= 1}
            className="p-2 rounded-md hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Previous page (←)"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          
          <div className="flex items-center space-x-2">
            <input
              type="number"
              value={currentPage}
              onChange={(e) => {
                const page = parseInt(e.target.value) || 1;
                goToPage(page);
              }}
              className="w-16 px-2 py-1 text-sm border border-gray-300 rounded text-center"
              min={1}
              max={numPages}
            />
            <span className="text-sm text-gray-600">of {numPages}</span>
          </div>
          
          <button
            onClick={goToNextPage}
            disabled={currentPage >= numPages}
            className="p-2 rounded-md hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Next page (→)"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        <div className="flex items-center space-x-2">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search in document..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Zoom controls */}
          <button
            onClick={zoomOut}
            className="p-2 rounded-md hover:bg-gray-200"
            title="Zoom out (Ctrl+-)"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          
          <span className="text-sm text-gray-600 min-w-[4rem] text-center">
            {Math.round(scale * 100)}%
          </span>
          
          <button
            onClick={zoomIn}
            className="p-2 rounded-md hover:bg-gray-200"
            title="Zoom in (Ctrl++)"
          >
            <ZoomIn className="w-4 h-4" />
          </button>

          {/* Rotate */}
          <button
            onClick={rotateDocument}
            className="p-2 rounded-md hover:bg-gray-200"
            title="Rotate document"
          >
            <RotateCw className="w-4 h-4" />
          </button>

          {/* Download */}
          <button
            onClick={downloadDocument}
            className="p-2 rounded-md hover:bg-gray-200"
            title="Download document"
          >
            <Download className="w-4 h-4" />
          </button>

          {/* Fullscreen */}
          <button
            onClick={toggleFullscreen}
            className="p-2 rounded-md hover:bg-gray-200"
            title="Toggle fullscreen (Ctrl+F)"
          >
            {isFullscreen ? (
              <Minimize2 className="w-4 h-4" />
            ) : (
              <Maximize2 className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {/* Document viewer */}
      <div className="flex-1 overflow-auto bg-gray-100 p-4">
        {isLoading && (
          <div className="flex items-center justify-center h-96">
            <LoadingSpinner size="lg" />
          </div>
        )}
        
        <div className="flex justify-center">
          <Document
            file={documentUrl}
            onLoadSuccess={onDocumentLoadSuccess}
            onLoadError={onDocumentLoadError}
            loading={<LoadingSpinner size="lg" />}
            className="shadow-lg"
          >
            <div
              ref={(el) => {
                if (el) pageRefs.current[currentPage] = el;
              }}
              onMouseUp={handleTextSelection}
              className="relative"
            >
              <Page
                pageNumber={currentPage}
                scale={scale}
                rotate={rotation}
                renderTextLayer={true}
                renderAnnotationLayer={true}
                className="border border-gray-300 bg-white"
              />
              
              {/* Render annotations for current page */}
              {annotations
                .filter(annotation => annotation.pageNumber === currentPage)
                .map(annotation => (
                  <div
                    key={annotation.id}
                    className="absolute border-2 border-yellow-400 bg-yellow-200 bg-opacity-30 cursor-pointer"
                    style={{
                      left: annotation.x * scale,
                      top: annotation.y * scale,
                      width: annotation.width * scale,
                      height: annotation.height * scale,
                    }}
                    title={`${annotation.userName}: ${annotation.comment || annotation.text}`}
                  />
                ))
              }
            </div>
          </Document>
        </div>
      </div>

      {/* Status bar */}
      <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 text-sm text-gray-600">
        <div className="flex justify-between items-center">
          <span>{documentName}</span>
          <span>Page {currentPage} of {numPages}</span>
        </div>
      </div>
    </div>
  );
};

export default DocumentViewer;