'use client';

import React, { useState, useCallback, useRef, useEffect, useMemo } from 'react';
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
  Minimize2,
  Target
} from 'lucide-react';
import { DocumentDifference, ClauseSimilarity, TextPosition } from '@/types';
import LoadingSpinner from '../ui/LoadingSpinner';

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

interface EnhancedDocumentViewerProps {
  documentUrl: string;
  documentName: string;
  documentId: string;
  differences?: DocumentDifference[];
  similarities?: ClauseSimilarity[];
  selectedDifference?: DocumentDifference | null;
  selectedSimilarity?: ClauseSimilarity | null;
  highlightDifferences?: boolean;
  highlightSimilarities?: boolean;
  syncScrolling?: boolean;
  onTextSelect?: (selectedText: string, pageNumber: number) => void;
  onScrollSync?: (pageNumber: number, scrollTop: number) => void;
  className?: string;
}

interface Highlight {
  id: string;
  type: 'difference' | 'similarity';
  position: TextPosition;
  content: string;
  severity?: string;
  similarityScore?: number;
  isSelected?: boolean;
}

export const EnhancedDocumentViewer: React.FC<EnhancedDocumentViewerProps> = ({
  documentUrl,
  documentName,
  documentId,
  differences = [],
  similarities = [],
  selectedDifference,
  selectedSimilarity,
  highlightDifferences = true,
  highlightSimilarities = true,
  syncScrolling = false,
  onTextSelect,
  onScrollSync,
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
  
  const containerRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const pageRefs = useRef<{ [key: number]: HTMLDivElement }>({});

  // Create highlights from differences and similarities
  const highlights = useMemo(() => {
    const highlightList: Highlight[] = [];

    if (highlightDifferences) {
      differences.forEach(diff => {
        // Check if this difference applies to this document
        const position = documentId === diff.document1Position?.pageNumber ? 
          diff.document1Position : 
          documentId === diff.document2Position?.pageNumber ? 
            diff.document2Position : null;

        if (position) {
          highlightList.push({
            id: `diff-${diff.id}`,
            type: 'difference',
            position,
            content: diff.description,
            severity: diff.severity,
            isSelected: selectedDifference?.id === diff.id
          });
        }
      });
    }

    if (highlightSimilarities) {
      similarities.forEach(sim => {
        // Check if this similarity applies to this document
        const isDoc1 = documentId === sim.document1Clause.id;
        const position = isDoc1 ? sim.document1Clause.position : sim.document2Clause.position;
        const content = isDoc1 ? sim.document1Clause.content : sim.document2Clause.content;

        if (position) {
          highlightList.push({
            id: `sim-${sim.id}`,
            type: 'similarity',
            position,
            content,
            similarityScore: sim.similarityScore,
            isSelected: selectedSimilarity?.id === sim.id
          });
        }
      });
    }

    return highlightList;
  }, [differences, similarities, selectedDifference, selectedSimilarity, highlightDifferences, highlightSimilarities, documentId]);

  // Navigate to selected item
  useEffect(() => {
    if (selectedDifference || selectedSimilarity) {
      const selectedItem = selectedDifference || selectedSimilarity;
      if (!selectedItem) return;

      let targetPage: number | undefined;
      
      if (selectedDifference) {
        const position = documentId === selectedDifference.document1Position?.pageNumber ? 
          selectedDifference.document1Position : selectedDifference.document2Position;
        targetPage = position?.pageNumber;
      } else if (selectedSimilarity) {
        const isDoc1 = documentId === selectedSimilarity.document1Clause.id;
        const position = isDoc1 ? selectedSimilarity.document1Clause.position : selectedSimilarity.document2Clause.position;
        targetPage = position?.pageNumber;
      }

      if (targetPage && targetPage !== currentPage) {
        setCurrentPage(targetPage);
      }
    }
  }, [selectedDifference, selectedSimilarity, documentId, currentPage]);

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
    const newPage = Math.max(1, currentPage - 1);
    setCurrentPage(newPage);
    if (syncScrolling && onScrollSync) {
      onScrollSync(newPage, 0);
    }
  }, [currentPage, syncScrolling, onScrollSync]);

  const goToNextPage = useCallback(() => {
    const newPage = Math.min(numPages, currentPage + 1);
    setCurrentPage(newPage);
    if (syncScrolling && onScrollSync) {
      onScrollSync(newPage, 0);
    }
  }, [numPages, currentPage, syncScrolling, onScrollSync]);

  const goToPage = useCallback((page: number) => {
    if (page >= 1 && page <= numPages) {
      setCurrentPage(page);
      if (syncScrolling && onScrollSync) {
        onScrollSync(page, 0);
      }
    }
  }, [numPages, syncScrolling, onScrollSync]);

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
      onTextSelect?.(selection.toString(), currentPage);
    }
  }, [currentPage, onTextSelect]);

  // Handle scroll sync
  const handleScroll = useCallback((event: React.UIEvent<HTMLDivElement>) => {
    if (syncScrolling && onScrollSync) {
      const scrollTop = event.currentTarget.scrollTop;
      onScrollSync(currentPage, scrollTop);
    }
  }, [syncScrolling, onScrollSync, currentPage]);

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

  // Get highlight style
  const getHighlightStyle = (highlight: Highlight) => {
    const baseStyle = {
      position: 'absolute' as const,
      left: highlight.position.boundingBox?.x || 0,
      top: highlight.position.boundingBox?.y || 0,
      width: highlight.position.boundingBox?.width || 100,
      height: highlight.position.boundingBox?.height || 20,
      pointerEvents: 'none' as const,
      borderRadius: '2px',
      transition: 'all 0.2s ease'
    };

    if (highlight.isSelected) {
      return {
        ...baseStyle,
        backgroundColor: 'rgba(59, 130, 246, 0.3)',
        border: '2px solid rgb(59, 130, 246)',
        boxShadow: '0 0 0 2px rgba(59, 130, 246, 0.2)'
      };
    }

    if (highlight.type === 'difference') {
      switch (highlight.severity) {
        case 'high':
          return { ...baseStyle, backgroundColor: 'rgba(239, 68, 68, 0.2)', border: '1px solid rgba(239, 68, 68, 0.4)' };
        case 'medium':
          return { ...baseStyle, backgroundColor: 'rgba(245, 158, 11, 0.2)', border: '1px solid rgba(245, 158, 11, 0.4)' };
        case 'low':
          return { ...baseStyle, backgroundColor: 'rgba(34, 197, 94, 0.2)', border: '1px solid rgba(34, 197, 94, 0.4)' };
        default:
          return { ...baseStyle, backgroundColor: 'rgba(156, 163, 175, 0.2)', border: '1px solid rgba(156, 163, 175, 0.4)' };
      }
    } else {
      // Similarity highlight
      const opacity = (highlight.similarityScore || 0.5) * 0.3;
      return {
        ...baseStyle,
        backgroundColor: `rgba(34, 197, 94, ${opacity})`,
        border: '1px solid rgba(34, 197, 94, 0.4)'
      };
    }
  };

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

          {/* Highlight indicator */}
          {highlights.filter(h => h.position.pageNumber === currentPage).length > 0 && (
            <div className="flex items-center space-x-1 ml-4">
              <Target className="w-4 h-4 text-blue-500" />
              <span className="text-xs text-blue-600">
                {highlights.filter(h => h.position.pageNumber === currentPage).length} highlights
              </span>
            </div>
          )}
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
      <div 
        ref={scrollContainerRef}
        className="flex-1 overflow-auto bg-gray-100 p-4"
        onScroll={handleScroll}
      >
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
              
              {/* Render highlights for current page */}
              {highlights
                .filter(highlight => highlight.position.pageNumber === currentPage)
                .map(highlight => (
                  <div
                    key={highlight.id}
                    style={getHighlightStyle(highlight)}
                    title={highlight.content}
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
          <div className="flex items-center space-x-4">
            {highlights.length > 0 && (
              <span className="text-blue-600">
                {highlights.length} highlights total
              </span>
            )}
            <span>Page {currentPage} of {numPages}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedDocumentViewer;