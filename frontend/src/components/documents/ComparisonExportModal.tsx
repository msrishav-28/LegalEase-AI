'use client';

import React, { useState } from 'react';
import { 
  X, 
  Download, 
  FileText, 
  File, 
  Globe, 
  Code,
  Check,
  AlertCircle
} from 'lucide-react';
import { ComparisonExport, DocumentComparison } from '@/types';
import { documentApi } from '@/lib/api';
import LoadingSpinner from '../ui/LoadingSpinner';

interface ComparisonExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  comparison: DocumentComparison;
  className?: string;
}

interface ExportOptions extends ComparisonExport {
  includeMetrics: boolean;
  includeSummary: boolean;
  includeHighlights: boolean;
  sections: string[];
  customFilename?: string;
}

export const ComparisonExportModal: React.FC<ComparisonExportModalProps> = ({
  isOpen,
  onClose,
  comparison,
  className = ''
}) => {
  const [exportOptions, setExportOptions] = useState<ExportOptions>({
    format: 'pdf',
    includeHighlights: true,
    includeSummary: true,
    includeMetrics: true,
    sections: []
  });

  const [isExporting, setIsExporting] = useState<boolean>(false);
  const [exportError, setExportError] = useState<string | null>(null);
  const [exportSuccess, setExportSuccess] = useState<boolean>(false);

  // Available sections from the comparison
  const availableSections = React.useMemo(() => {
    const sections = new Set<string>();
    
    comparison.differences.forEach(diff => {
      if (diff.section) sections.add(diff.section);
    });
    
    comparison.similarities.forEach(sim => {
      if (sim.document1Clause.section) sections.add(sim.document1Clause.section);
      if (sim.document2Clause.section) sections.add(sim.document2Clause.section);
    });
    
    return Array.from(sections).sort();
  }, [comparison]);

  // Format options
  const formatOptions = [
    {
      value: 'pdf',
      label: 'PDF Document',
      icon: FileText,
      description: 'Professional report with formatting and highlights'
    },
    {
      value: 'docx',
      label: 'Word Document',
      icon: File,
      description: 'Editable document for further customization'
    },
    {
      value: 'html',
      label: 'HTML Report',
      icon: Globe,
      description: 'Web-based report for online sharing'
    },
    {
      value: 'json',
      label: 'JSON Data',
      icon: Code,
      description: 'Raw data for programmatic processing'
    }
  ] as const;

  // Handle export
  const handleExport = async () => {
    setIsExporting(true);
    setExportError(null);
    setExportSuccess(false);

    try {
      const response = await documentApi.exportComparison(
        comparison.id,
        exportOptions.format,
        {
          includeHighlights: exportOptions.includeHighlights,
          includeSummary: exportOptions.includeSummary,
          includeMetrics: exportOptions.includeMetrics,
          sections: exportOptions.sections.length > 0 ? exportOptions.sections : undefined
        }
      );

      if (response.success && response.data) {
        // Create and trigger download
        const mimeTypes = {
          pdf: 'application/pdf',
          docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          html: 'text/html',
          json: 'application/json'
        };

        const blob = new Blob([response.data], { 
          type: mimeTypes[exportOptions.format]
        });
        
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        
        const filename = exportOptions.customFilename || 
          `comparison-${comparison.document1.name}-vs-${comparison.document2.name}`;
        link.download = `${filename}.${exportOptions.format}`;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        setExportSuccess(true);
        setTimeout(() => {
          onClose();
          setExportSuccess(false);
        }, 2000);
      } else {
        setExportError(response.error || 'Failed to export comparison');
      }
    } catch (error) {
      setExportError('An unexpected error occurred during export');
    } finally {
      setIsExporting(false);
    }
  };

  // Handle section selection
  const handleSectionToggle = (section: string) => {
    setExportOptions(prev => ({
      ...prev,
      sections: prev.sections.includes(section)
        ? prev.sections.filter(s => s !== section)
        : [...prev.sections, section]
    }));
  };

  const handleSelectAllSections = () => {
    setExportOptions(prev => ({
      ...prev,
      sections: prev.sections.length === availableSections.length ? [] : [...availableSections]
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div 
          className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75"
          onClick={onClose}
        />

        {/* Modal */}
        <div className={`inline-block w-full max-w-2xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg ${className}`}>
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900">
                Export Comparison
              </h3>
              <p className="text-sm text-gray-600">
                {comparison.document1.name} vs {comparison.document2.name}
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Export Success */}
          {exportSuccess && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center">
                <Check className="w-5 h-5 text-green-500 mr-2" />
                <span className="text-sm text-green-800">
                  Export completed successfully!
                </span>
              </div>
            </div>
          )}

          {/* Export Error */}
          {exportError && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
                <span className="text-sm text-red-800">{exportError}</span>
              </div>
            </div>
          )}

          <div className="space-y-6">
            {/* Format Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Export Format
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {formatOptions.map((option) => {
                  const Icon = option.icon;
                  return (
                    <div
                      key={option.value}
                      onClick={() => setExportOptions(prev => ({ ...prev, format: option.value }))}
                      className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                        exportOptions.format === option.value
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <Icon className={`w-5 h-5 mt-0.5 ${
                          exportOptions.format === option.value ? 'text-blue-600' : 'text-gray-400'
                        }`} />
                        <div>
                          <h4 className={`text-sm font-medium ${
                            exportOptions.format === option.value ? 'text-blue-900' : 'text-gray-900'
                          }`}>
                            {option.label}
                          </h4>
                          <p className="text-xs text-gray-600 mt-1">
                            {option.description}
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Content Options */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Include Content
              </label>
              <div className="space-y-3">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={exportOptions.includeSummary}
                    onChange={(e) => setExportOptions(prev => ({ 
                      ...prev, 
                      includeSummary: e.target.checked 
                    }))}
                    className="mr-3 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <div>
                    <span className="text-sm text-gray-900">Executive Summary</span>
                    <p className="text-xs text-gray-600">
                      High-level overview of comparison results
                    </p>
                  </div>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={exportOptions.includeMetrics}
                    onChange={(e) => setExportOptions(prev => ({ 
                      ...prev, 
                      includeMetrics: e.target.checked 
                    }))}
                    className="mr-3 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <div>
                    <span className="text-sm text-gray-900">Comparison Metrics</span>
                    <p className="text-xs text-gray-600">
                      Similarity scores and statistical analysis
                    </p>
                  </div>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={exportOptions.includeHighlights}
                    onChange={(e) => setExportOptions(prev => ({ 
                      ...prev, 
                      includeHighlights: e.target.checked 
                    }))}
                    className="mr-3 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <div>
                    <span className="text-sm text-gray-900">Visual Highlights</span>
                    <p className="text-xs text-gray-600">
                      Color-coded differences and similarities
                    </p>
                  </div>
                </label>
              </div>
            </div>

            {/* Section Selection */}
            {availableSections.length > 0 && (
              <div>
                <div className="flex items-center justify-between mb-3">
                  <label className="text-sm font-medium text-gray-700">
                    Sections to Include
                  </label>
                  <button
                    onClick={handleSelectAllSections}
                    className="text-xs text-blue-600 hover:text-blue-800"
                  >
                    {exportOptions.sections.length === availableSections.length ? 'Deselect All' : 'Select All'}
                  </button>
                </div>
                
                <div className="max-h-32 overflow-y-auto border border-gray-200 rounded-md">
                  <div className="p-2 space-y-1">
                    {availableSections.map((section) => (
                      <label key={section} className="flex items-center">
                        <input
                          type="checkbox"
                          checked={exportOptions.sections.includes(section)}
                          onChange={() => handleSectionToggle(section)}
                          className="mr-2 h-3 w-3 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <span className="text-xs text-gray-700">{section}</span>
                      </label>
                    ))}
                  </div>
                </div>
                
                {exportOptions.sections.length === 0 && (
                  <p className="text-xs text-gray-500 mt-1">
                    All sections will be included when none are selected
                  </p>
                )}
              </div>
            )}

            {/* Custom Filename */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Custom Filename (optional)
              </label>
              <input
                type="text"
                value={exportOptions.customFilename || ''}
                onChange={(e) => setExportOptions(prev => ({ 
                  ...prev, 
                  customFilename: e.target.value 
                }))}
                placeholder={`comparison-${comparison.document1.name}-vs-${comparison.document2.name}`}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                File extension will be added automatically
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end space-x-3 mt-8 pt-6 border-t border-gray-200">
            <button
              onClick={onClose}
              disabled={isExporting}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleExport}
              disabled={isExporting}
              className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {isExporting ? (
                <>
                  <LoadingSpinner size="sm" />
                  <span>Exporting...</span>
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  <span>Export</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComparisonExportModal;