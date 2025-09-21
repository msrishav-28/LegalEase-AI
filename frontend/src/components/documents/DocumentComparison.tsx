'use client';

import React, { useState, useCallback, useEffect, useMemo } from 'react';
import { 
  ArrowLeftRight, 
  Download, 
  Filter, 
  Search, 
  Eye, 
  EyeOff,
  ChevronDown,
  ChevronRight,
  AlertTriangle,
  CheckCircle,
  XCircle,
  BarChart3,
  FileText,
  Settings
} from 'lucide-react';
import { DocumentViewer } from './DocumentViewer';
import { EnhancedDocumentViewer } from './EnhancedDocumentViewer';
import { ClauseSimilarityVisualization } from './ClauseSimilarityVisualization';
import { ComparisonNavigation } from './ComparisonNavigation';
import { documentApi } from '@/lib/api';
import { 
  Document, 
  DocumentComparison as DocumentComparisonType, 
  DocumentDifference, 
  ClauseSimilarity,
  ComparisonExport 
} from '@/types';
import LoadingSpinner from '../ui/LoadingSpinner';

interface DocumentComparisonProps {
  document1: Document;
  document2: Document;
  comparisonId?: string;
  onComparisonComplete?: (comparison: DocumentComparisonType) => void;
  className?: string;
}

interface FilterOptions {
  showDifferences: boolean;
  showSimilarities: boolean;
  differenceTypes: string[];
  severityLevels: string[];
  categories: string[];
  similarityThreshold: number;
}

interface ViewOptions {
  layout: 'side-by-side' | 'overlay' | 'unified';
  showLineNumbers: boolean;
  showMetadata: boolean;
  highlightDifferences: boolean;
  highlightSimilarities: boolean;
  syncScrolling: boolean;
  showDoc1: boolean;
  showDoc2: boolean;
}

export const DocumentComparison: React.FC<DocumentComparisonProps> = ({
  document1,
  document2,
  comparisonId,
  onComparisonComplete,
  className = ''
}) => {
  const [comparison, setComparison] = useState<DocumentComparisonType | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedDifference, setSelectedDifference] = useState<DocumentDifference | null>(null);
  const [selectedSimilarity, setSelectedSimilarity] = useState<ClauseSimilarity | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [isExporting, setIsExporting] = useState<boolean>(false);
  
  const [filters, setFilters] = useState<FilterOptions>({
    showDifferences: true,
    showSimilarities: true,
    differenceTypes: ['added', 'removed', 'modified'],
    severityLevels: ['high', 'medium', 'low'],
    categories: ['clause', 'term', 'obligation', 'party', 'date', 'amount', 'other'],
    similarityThreshold: 0.7
  });

  const [viewOptions, setViewOptions] = useState<ViewOptions>({
    layout: 'side-by-side',
    showLineNumbers: true,
    showMetadata: true,
    highlightDifferences: true,
    highlightSimilarities: true,
    syncScrolling: true,
    showDoc1: true,
    showDoc2: true
  });

  const [showFilters, setShowFilters] = useState<boolean>(false);
  const [showSettings, setShowSettings] = useState<boolean>(false);
  const [showSimilarityVisualization, setShowSimilarityVisualization] = useState<boolean>(false);
  const [showNavigation, setShowNavigation] = useState<boolean>(false);
  const [navigationIndex, setNavigationIndex] = useState<number>(0);
  const [isAutoNavigating, setIsAutoNavigating] = useState<boolean>(false);

  // Load or create comparison
  useEffect(() => {
    const loadComparison = async () => {
      if (comparisonId) {
        // Load existing comparison
        setIsLoading(true);
        try {
          const response = await documentApi.getComparison(comparisonId);
          if (response.success && response.data) {
            setComparison(response.data);
            onComparisonComplete?.(response.data);
          } else {
            setError(response.error || 'Failed to load comparison');
          }
        } catch (err) {
          setError('Failed to load comparison');
        } finally {
          setIsLoading(false);
        }
      } else {
        // Create new comparison
        await createComparison();
      }
    };

    loadComparison();
  }, [comparisonId, document1.id, document2.id]);

  const createComparison = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await documentApi.compareDocuments(document1.id, document2.id, {
        includeStructural: true,
        includeContent: true,
        includeLegal: true,
        similarityThreshold: filters.similarityThreshold
      });

      if (response.success && response.data) {
        setComparison(response.data);
        onComparisonComplete?.(response.data);
      } else {
        setError(response.error || 'Failed to create comparison');
      }
    } catch (err) {
      setError('Failed to create comparison');
    } finally {
      setIsLoading(false);
    }
  };

  // Filter differences and similarities based on current filters
  const filteredDifferences = useMemo(() => {
    if (!comparison || !filters.showDifferences) return [];
    
    return comparison.differences.filter(diff => {
      if (!filters.differenceTypes.includes(diff.type)) return false;
      if (!filters.severityLevels.includes(diff.severity)) return false;
      if (!filters.categories.includes(diff.category)) return false;
      
      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        return (
          diff.description.toLowerCase().includes(searchLower) ||
          diff.section.toLowerCase().includes(searchLower) ||
          diff.document1Content?.toLowerCase().includes(searchLower) ||
          diff.document2Content?.toLowerCase().includes(searchLower)
        );
      }
      
      return true;
    });
  }, [comparison, filters, searchTerm]);

  const filteredSimilarities = useMemo(() => {
    if (!comparison || !filters.showSimilarities) return [];
    
    return comparison.similarities.filter(sim => {
      if (sim.similarityScore < filters.similarityThreshold) return false;
      
      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        return (
          sim.document1Clause.content.toLowerCase().includes(searchLower) ||
          sim.document2Clause.content.toLowerCase().includes(searchLower) ||
          sim.document1Clause.section.toLowerCase().includes(searchLower) ||
          sim.document2Clause.section.toLowerCase().includes(searchLower)
        );
      }
      
      return true;
    });
  }, [comparison, filters, searchTerm]);

  // Handle difference selection
  const handleDifferenceSelect = useCallback((difference: DocumentDifference) => {
    setSelectedDifference(difference);
    setSelectedSimilarity(null);
    
    // Navigate to the difference location in documents
    if (difference.document1Position || difference.document2Position) {
      // Scroll to the difference location
      const position = difference.document1Position || difference.document2Position;
      if (position) {
        // This would trigger navigation in the document viewers
        // Implementation would depend on document viewer integration
      }
    }
  }, []);

  // Handle similarity selection
  const handleSimilaritySelect = useCallback((similarity: ClauseSimilarity) => {
    setSelectedSimilarity(similarity);
    setSelectedDifference(null);
    
    // Navigate to the similarity location in documents
    if (similarity.document1Clause.position || similarity.document2Clause.position) {
      // Scroll to the similarity location
      const position = similarity.document1Clause.position || similarity.document2Clause.position;
      if (position) {
        // This would trigger navigation in the document viewers
        // Implementation would depend on document viewer integration
      }
    }
  }, []);

  // Export comparison
  const handleExport = async (format: ComparisonExport['format']) => {
    if (!comparison) return;
    
    setIsExporting(true);
    try {
      const response = await documentApi.exportComparison(comparison.id, format, {
        includeHighlights: viewOptions.highlightDifferences || viewOptions.highlightSimilarities,
        includeSummary: true,
        includeMetrics: true
      });

      if (response.success && response.data) {
        // Handle file download
        const blob = new Blob([response.data], { 
          type: format === 'pdf' ? 'application/pdf' : 
                format === 'docx' ? 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' :
                format === 'html' ? 'text/html' : 'application/json'
        });
        
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `comparison-${document1.name}-vs-${document2.name}.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } else {
        setError(response.error || 'Failed to export comparison');
      }
    } catch (err) {
      setError('Failed to export comparison');
    } finally {
      setIsExporting(false);
    }
  };

  // Get severity color
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  // Get difference type icon
  const getDifferenceIcon = (type: string) => {
    switch (type) {
      case 'added': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'removed': return <XCircle className="w-4 h-4 text-red-500" />;
      case 'modified': return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      default: return <FileText className="w-4 h-4 text-gray-500" />;
    }
  };

  if (isLoading) {
    return (
      <div className={`flex items-center justify-center h-96 ${className}`}>
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">Comparing documents...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`flex items-center justify-center h-96 bg-red-50 rounded-lg ${className}`}>
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-red-800 mb-2">Comparison Failed</h3>
          <p className="text-red-600">{error}</p>
          <button
            onClick={createComparison}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
          >
            Retry Comparison
          </button>
        </div>
      </div>
    );
  }

  if (!comparison) {
    return null;
  }

  return (
    <div className={`flex flex-col h-full bg-white ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center space-x-4">
          <ArrowLeftRight className="w-5 h-5 text-gray-500" />
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Document Comparison</h2>
            <p className="text-sm text-gray-600">
              {document1.name} vs {document2.name}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search differences..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Filters */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`p-2 rounded-md border ${showFilters ? 'bg-blue-50 border-blue-200' : 'bg-white border-gray-300'} hover:bg-gray-50`}
            title="Filter options"
          >
            <Filter className="w-4 h-4" />
          </button>

          {/* Navigation */}
          <button
            onClick={() => setShowNavigation(!showNavigation)}
            className={`p-2 rounded-md border ${showNavigation ? 'bg-blue-50 border-blue-200' : 'bg-white border-gray-300'} hover:bg-gray-50`}
            title="Navigation controls"
          >
            <ArrowLeftRight className="w-4 h-4" />
          </button>

          {/* Settings */}
          <button
            onClick={() => setShowSettings(!showSettings)}
            className={`p-2 rounded-md border ${showSettings ? 'bg-blue-50 border-blue-200' : 'bg-white border-gray-300'} hover:bg-gray-50`}
            title="View settings"
          >
            <Settings className="w-4 h-4" />
          </button>

          {/* Export */}
          <div className="relative">
            <button
              onClick={() => handleExport('pdf')}
              disabled={isExporting}
              className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              title="Export comparison"
            >
              <Download className="w-4 h-4" />
              <span>Export</span>
            </button>
          </div>
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Show
              </label>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.showDifferences}
                    onChange={(e) => setFilters(prev => ({ ...prev, showDifferences: e.target.checked }))}
                    className="mr-2"
                  />
                  <span className="text-sm">Differences</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.showSimilarities}
                    onChange={(e) => setFilters(prev => ({ ...prev, showSimilarities: e.target.checked }))}
                    className="mr-2"
                  />
                  <span className="text-sm">Similarities</span>
                </label>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Severity
              </label>
              <div className="space-y-2">
                {['high', 'medium', 'low'].map(level => (
                  <label key={level} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={filters.severityLevels.includes(level)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setFilters(prev => ({ 
                            ...prev, 
                            severityLevels: [...prev.severityLevels, level] 
                          }));
                        } else {
                          setFilters(prev => ({ 
                            ...prev, 
                            severityLevels: prev.severityLevels.filter(l => l !== level) 
                          }));
                        }
                      }}
                      className="mr-2"
                    />
                    <span className={`text-sm capitalize ${getSeverityColor(level).split(' ')[0]}`}>
                      {level}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Similarity Threshold
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={filters.similarityThreshold}
                onChange={(e) => setFilters(prev => ({ 
                  ...prev, 
                  similarityThreshold: parseFloat(e.target.value) 
                }))}
                className="w-full"
              />
              <div className="text-sm text-gray-600 mt-1">
                {Math.round(filters.similarityThreshold * 100)}%
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Navigation Panel */}
      {showNavigation && (
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <ComparisonNavigation
            differences={filteredDifferences}
            similarities={filteredSimilarities}
            currentIndex={navigationIndex}
            onNavigate={setNavigationIndex}
            onItemSelect={(item) => {
              if ('type' in item && ['added', 'removed', 'modified'].includes(item.type)) {
                handleDifferenceSelect(item as DocumentDifference);
              } else {
                handleSimilaritySelect(item as ClauseSimilarity);
              }
            }}
            onAutoNavigate={setIsAutoNavigating}
            className="max-w-md mx-auto"
          />
        </div>
      )}

      {/* Settings Panel */}
      {showSettings && (
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Layout
              </label>
              <select
                value={viewOptions.layout}
                onChange={(e) => setViewOptions(prev => ({ 
                  ...prev, 
                  layout: e.target.value as ViewOptions['layout'] 
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="side-by-side">Side by Side</option>
                <option value="overlay">Overlay</option>
                <option value="unified">Unified</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Display Options
              </label>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={viewOptions.highlightDifferences}
                    onChange={(e) => setViewOptions(prev => ({ 
                      ...prev, 
                      highlightDifferences: e.target.checked 
                    }))}
                    className="mr-2"
                  />
                  <span className="text-sm">Highlight Differences</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={viewOptions.highlightSimilarities}
                    onChange={(e) => setViewOptions(prev => ({ 
                      ...prev, 
                      highlightSimilarities: e.target.checked 
                    }))}
                    className="mr-2"
                  />
                  <span className="text-sm">Highlight Similarities</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={viewOptions.syncScrolling}
                    onChange={(e) => setViewOptions(prev => ({ 
                      ...prev, 
                      syncScrolling: e.target.checked 
                    }))}
                    className="mr-2"
                  />
                  <span className="text-sm">Sync Scrolling</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar - Differences and Similarities */}
        <div className="w-80 border-r border-gray-200 bg-gray-50 overflow-y-auto">
          {/* Metrics Summary */}
          <div className="p-4 border-b border-gray-200">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Comparison Metrics</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Overall Similarity</span>
                <span className="font-medium">
                  {Math.round(comparison.comparisonMetrics.overallSimilarity * 100)}%
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Total Differences</span>
                <span className="font-medium">{comparison.comparisonMetrics.totalDifferences}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Critical Issues</span>
                <span className="font-medium text-red-600">
                  {comparison.comparisonMetrics.criticalDifferences}
                </span>
              </div>
            </div>
          </div>

          {/* Differences List */}
          {filters.showDifferences && (
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-medium text-gray-900">
                  Differences ({filteredDifferences.length})
                </h3>
                <BarChart3 className="w-4 h-4 text-gray-500" />
              </div>
              
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {filteredDifferences.map((difference) => (
                  <div
                    key={difference.id}
                    onClick={() => handleDifferenceSelect(difference)}
                    className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                      selectedDifference?.id === difference.id
                        ? 'border-blue-300 bg-blue-50'
                        : `border-gray-200 hover:bg-gray-50 ${getSeverityColor(difference.severity)}`
                    }`}
                  >
                    <div className="flex items-start space-x-2">
                      {getDifferenceIcon(difference.type)}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="text-xs font-medium text-gray-500 uppercase">
                            {difference.type}
                          </span>
                          <span className="text-xs text-gray-400">
                            {difference.category}
                          </span>
                        </div>
                        <p className="text-sm text-gray-900 line-clamp-2">
                          {difference.description}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          Section: {difference.section}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Similarities List */}
          {filters.showSimilarities && (
            <div className="p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-medium text-gray-900">
                  Similarities ({filteredSimilarities.length})
                </h3>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setShowSimilarityVisualization(!showSimilarityVisualization)}
                    className="p-1 rounded hover:bg-gray-200"
                    title="Toggle similarity visualization"
                  >
                    <BarChart3 className="w-4 h-4 text-blue-500" />
                  </button>
                  <CheckCircle className="w-4 h-4 text-green-500" />
                </div>
              </div>
              
              {showSimilarityVisualization ? (
                <div className="mb-4">
                  <ClauseSimilarityVisualization
                    similarities={filteredSimilarities}
                    comparison={comparison}
                    selectedSimilarity={selectedSimilarity}
                    onSimilaritySelect={handleSimilaritySelect}
                    className="max-h-96 overflow-y-auto"
                  />
                </div>
              ) : (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {filteredSimilarities.map((similarity) => (
                    <div
                      key={similarity.id}
                      onClick={() => handleSimilaritySelect(similarity)}
                      className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                        selectedSimilarity?.id === similarity.id
                          ? 'border-green-300 bg-green-50'
                          : 'border-gray-200 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-medium text-green-600 uppercase">
                          {similarity.type}
                        </span>
                        <span className="text-xs text-gray-500">
                          {Math.round(similarity.similarityScore * 100)}%
                        </span>
                      </div>
                      <p className="text-sm text-gray-900 line-clamp-2">
                        {similarity.document1Clause.content.substring(0, 100)}...
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Sections: {similarity.document1Clause.section} ↔ {similarity.document2Clause.section}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Document Viewers */}
        <div className="flex-1 flex">
          {viewOptions.layout === 'side-by-side' && (
            <>
              <div className="flex-1 border-r border-gray-200">
                <div className="p-2 bg-gray-50 border-b border-gray-200">
                  <h4 className="text-sm font-medium text-gray-900">{document1.name}</h4>
                </div>
                <EnhancedDocumentViewer
                  documentUrl={`/api/documents/${document1.id}/content`}
                  documentName={document1.name}
                  documentId={document1.id}
                  differences={comparison.differences}
                  similarities={comparison.similarities}
                  selectedDifference={selectedDifference}
                  selectedSimilarity={selectedSimilarity}
                  highlightDifferences={viewOptions.highlightDifferences}
                  highlightSimilarities={viewOptions.highlightSimilarities}
                  syncScrolling={viewOptions.syncScrolling}
                  className="h-full"
                />
              </div>
              <div className="flex-1">
                <div className="p-2 bg-gray-50 border-b border-gray-200">
                  <h4 className="text-sm font-medium text-gray-900">{document2.name}</h4>
                </div>
                <EnhancedDocumentViewer
                  documentUrl={`/api/documents/${document2.id}/content`}
                  documentName={document2.name}
                  documentId={document2.id}
                  differences={comparison.differences}
                  similarities={comparison.similarities}
                  selectedDifference={selectedDifference}
                  selectedSimilarity={selectedSimilarity}
                  highlightDifferences={viewOptions.highlightDifferences}
                  highlightSimilarities={viewOptions.highlightSimilarities}
                  syncScrolling={viewOptions.syncScrolling}
                  className="h-full"
                />
              </div>
            </>
          )}
          
          {viewOptions.layout === 'overlay' && (
            <div className="flex-1 relative">
              <div className="p-2 bg-gray-50 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-medium text-gray-900">Overlay View</h4>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setViewOptions(prev => ({ ...prev, showDoc1: !prev.showDoc1 }))}
                      className={`px-3 py-1 text-xs rounded ${
                        viewOptions.showDoc1 ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {document1.name}
                    </button>
                    <button
                      onClick={() => setViewOptions(prev => ({ ...prev, showDoc2: !prev.showDoc2 }))}
                      className={`px-3 py-1 text-xs rounded ${
                        viewOptions.showDoc2 ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {document2.name}
                    </button>
                  </div>
                </div>
              </div>
              <div className="relative h-full">
                {viewOptions.showDoc1 && (
                  <div className="absolute inset-0" style={{ opacity: viewOptions.showDoc2 ? 0.7 : 1 }}>
                    <EnhancedDocumentViewer
                      documentUrl={`/api/documents/${document1.id}/content`}
                      documentName={document1.name}
                      documentId={document1.id}
                      differences={comparison.differences}
                      similarities={comparison.similarities}
                      selectedDifference={selectedDifference}
                      selectedSimilarity={selectedSimilarity}
                      highlightDifferences={viewOptions.highlightDifferences}
                      highlightSimilarities={viewOptions.highlightSimilarities}
                      className="h-full"
                    />
                  </div>
                )}
                {viewOptions.showDoc2 && (
                  <div className="absolute inset-0" style={{ opacity: viewOptions.showDoc1 ? 0.7 : 1 }}>
                    <EnhancedDocumentViewer
                      documentUrl={`/api/documents/${document2.id}/content`}
                      documentName={document2.name}
                      documentId={document2.id}
                      differences={comparison.differences}
                      similarities={comparison.similarities}
                      selectedDifference={selectedDifference}
                      selectedSimilarity={selectedSimilarity}
                      highlightDifferences={viewOptions.highlightDifferences}
                      highlightSimilarities={viewOptions.highlightSimilarities}
                      className="h-full"
                    />
                  </div>
                )}
              </div>
            </div>
          )}

          {viewOptions.layout === 'unified' && (
            <div className="flex-1">
              <div className="p-2 bg-gray-50 border-b border-gray-200">
                <h4 className="text-sm font-medium text-gray-900">Unified View</h4>
              </div>
              <div className="h-full overflow-y-auto">
                <UnifiedComparisonView
                  comparison={comparison}
                  selectedDifference={selectedDifference}
                  selectedSimilarity={selectedSimilarity}
                  onDifferenceSelect={handleDifferenceSelect}
                  onSimilaritySelect={handleSimilaritySelect}
                  highlightDifferences={viewOptions.highlightDifferences}
                  highlightSimilarities={viewOptions.highlightSimilarities}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Unified Comparison View Component
interface UnifiedComparisonViewProps {
  comparison: DocumentComparisonType;
  selectedDifference: DocumentDifference | null;
  selectedSimilarity: ClauseSimilarity | null;
  onDifferenceSelect: (difference: DocumentDifference) => void;
  onSimilaritySelect: (similarity: ClauseSimilarity) => void;
  highlightDifferences: boolean;
  highlightSimilarities: boolean;
}

const UnifiedComparisonView: React.FC<UnifiedComparisonViewProps> = ({
  comparison,
  selectedDifference,
  selectedSimilarity,
  onDifferenceSelect,
  onSimilaritySelect,
  highlightDifferences,
  highlightSimilarities
}) => {
  // Create a unified structure combining both documents
  const unifiedSections = useMemo(() => {
    const sections = new Map<string, {
      section: string;
      document1Content?: string;
      document2Content?: string;
      differences: DocumentDifference[];
      similarities: ClauseSimilarity[];
    }>();

    // Add differences to sections
    comparison.differences.forEach(diff => {
      if (!sections.has(diff.section)) {
        sections.set(diff.section, {
          section: diff.section,
          differences: [],
          similarities: []
        });
      }
      const section = sections.get(diff.section)!;
      section.differences.push(diff);
      if (diff.document1Content) section.document1Content = diff.document1Content;
      if (diff.document2Content) section.document2Content = diff.document2Content;
    });

    // Add similarities to sections
    comparison.similarities.forEach(sim => {
      const section1 = sim.document1Clause.section;
      const section2 = sim.document2Clause.section;
      
      [section1, section2].forEach(sectionName => {
        if (!sections.has(sectionName)) {
          sections.set(sectionName, {
            section: sectionName,
            differences: [],
            similarities: []
          });
        }
        const section = sections.get(sectionName)!;
        if (!section.similarities.find(s => s.id === sim.id)) {
          section.similarities.push(sim);
        }
      });
    });

    return Array.from(sections.values()).sort((a, b) => a.section.localeCompare(b.section));
  }, [comparison]);

  const getDifferenceHighlight = (difference: DocumentDifference) => {
    const isSelected = selectedDifference?.id === difference.id;
    const baseClasses = "p-3 rounded-lg border cursor-pointer transition-all duration-200";
    
    if (isSelected) {
      return `${baseClasses} border-blue-500 bg-blue-50 shadow-md`;
    }
    
    switch (difference.type) {
      case 'added':
        return `${baseClasses} border-green-200 bg-green-50 hover:bg-green-100`;
      case 'removed':
        return `${baseClasses} border-red-200 bg-red-50 hover:bg-red-100`;
      case 'modified':
        return `${baseClasses} border-yellow-200 bg-yellow-50 hover:bg-yellow-100`;
      default:
        return `${baseClasses} border-gray-200 bg-gray-50 hover:bg-gray-100`;
    }
  };

  const getSimilarityHighlight = (similarity: ClauseSimilarity) => {
    const isSelected = selectedSimilarity?.id === similarity.id;
    const baseClasses = "p-3 rounded-lg border cursor-pointer transition-all duration-200";
    
    if (isSelected) {
      return `${baseClasses} border-blue-500 bg-blue-50 shadow-md`;
    }
    
    return `${baseClasses} border-green-200 bg-green-50 hover:bg-green-100`;
  };

  return (
    <div className="p-6 space-y-6">
      <div className="text-center mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Unified Document Comparison
        </h3>
        <p className="text-sm text-gray-600">
          {comparison.document1.name} vs {comparison.document2.name}
        </p>
      </div>

      {unifiedSections.map((section) => (
        <div key={section.section} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
            <h4 className="text-md font-medium text-gray-900">{section.section}</h4>
          </div>
          
          <div className="p-4 space-y-4">
            {/* Differences in this section */}
            {highlightDifferences && section.differences.length > 0 && (
              <div>
                <h5 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
                  <AlertTriangle className="w-4 h-4 mr-2 text-yellow-500" />
                  Differences ({section.differences.length})
                </h5>
                <div className="space-y-3">
                  {section.differences.map((difference) => (
                    <div
                      key={difference.id}
                      onClick={() => onDifferenceSelect(difference)}
                      className={getDifferenceHighlight(difference)}
                    >
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0">
                          {difference.type === 'added' && <CheckCircle className="w-5 h-5 text-green-500" />}
                          {difference.type === 'removed' && <XCircle className="w-5 h-5 text-red-500" />}
                          {difference.type === 'modified' && <AlertTriangle className="w-5 h-5 text-yellow-500" />}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-2">
                            <span className="text-xs font-medium text-gray-500 uppercase">
                              {difference.type}
                            </span>
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                              difference.severity === 'high' 
                                ? 'bg-red-100 text-red-800'
                                : difference.severity === 'medium'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-green-100 text-green-800'
                            }`}>
                              {difference.severity}
                            </span>
                          </div>
                          <p className="text-sm text-gray-900 mb-2">{difference.description}</p>
                          
                          {difference.type === 'modified' && (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
                              <div>
                                <p className="text-xs text-gray-500 mb-1">{comparison.document1.name}</p>
                                <div className="p-2 bg-red-50 border border-red-200 rounded text-sm">
                                  {difference.document1Content}
                                </div>
                              </div>
                              <div>
                                <p className="text-xs text-gray-500 mb-1">{comparison.document2.name}</p>
                                <div className="p-2 bg-green-50 border border-green-200 rounded text-sm">
                                  {difference.document2Content}
                                </div>
                              </div>
                            </div>
                          )}
                          
                          {difference.type === 'added' && difference.document2Content && (
                            <div className="mt-3">
                              <p className="text-xs text-gray-500 mb-1">Added in {comparison.document2.name}</p>
                              <div className="p-2 bg-green-50 border border-green-200 rounded text-sm">
                                {difference.document2Content}
                              </div>
                            </div>
                          )}
                          
                          {difference.type === 'removed' && difference.document1Content && (
                            <div className="mt-3">
                              <p className="text-xs text-gray-500 mb-1">Removed from {comparison.document1.name}</p>
                              <div className="p-2 bg-red-50 border border-red-200 rounded text-sm">
                                {difference.document1Content}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Similarities in this section */}
            {highlightSimilarities && section.similarities.length > 0 && (
              <div>
                <h5 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
                  Similarities ({section.similarities.length})
                </h5>
                <div className="space-y-3">
                  {section.similarities.map((similarity) => (
                    <div
                      key={similarity.id}
                      onClick={() => onSimilaritySelect(similarity)}
                      className={getSimilarityHighlight(similarity)}
                    >
                      <div className="flex items-start space-x-3">
                        <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-2">
                            <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${
                              similarity.type === 'identical' 
                                ? 'bg-green-100 text-green-800'
                                : similarity.type === 'similar'
                                ? 'bg-blue-100 text-blue-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {similarity.type}
                            </span>
                            <span className="text-sm font-medium text-green-600">
                              {Math.round(similarity.similarityScore * 100)}%
                            </span>
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <p className="text-xs text-gray-500 mb-1">
                                {comparison.document1.name} - {similarity.document1Clause.section}
                              </p>
                              <div className="p-2 bg-green-50 border border-green-200 rounded text-sm">
                                {similarity.document1Clause.content}
                              </div>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500 mb-1">
                                {comparison.document2.name} - {similarity.document2Clause.section}
                              </p>
                              <div className="p-2 bg-green-50 border border-green-200 rounded text-sm">
                                {similarity.document2Clause.content}
                              </div>
                            </div>
                          </div>
                          
                          {similarity.differences && similarity.differences.length > 0 && (
                            <div className="mt-3">
                              <p className="text-xs text-gray-500 mb-1">Minor Differences:</p>
                              <ul className="text-xs text-gray-600 space-y-1">
                                {similarity.differences.slice(0, 3).map((diff, index) => (
                                  <li key={index} className="flex items-center space-x-1">
                                    <div className="w-1 h-1 bg-yellow-400 rounded-full" />
                                    <span>{diff}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      ))}

      {unifiedSections.length === 0 && (
        <div className="text-center py-12">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h4 className="text-lg font-medium text-gray-900 mb-2">
            No Comparison Data
          </h4>
          <p className="text-gray-600">
            No differences or similarities found between the documents.
          </p>
        </div>
      )}
    </div>
  );
};

export default DocumentComparison;