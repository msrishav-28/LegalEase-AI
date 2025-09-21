'use client';

import React, { useState, useMemo } from 'react';
import { 
  Search, 
  Filter, 
  MoreVertical, 
  Download, 
  Eye, 
  Trash2, 
  RefreshCw,
  FileText,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react';
import { cn, formatFileSize, formatDate, getJurisdictionColor } from '@/lib/utils';
import { Document, DocumentType, Jurisdiction, AnalysisStatus } from '@/types';

interface DocumentListProps {
  documents: Document[];
  onDocumentSelect?: (document: Document) => void;
  onDocumentDelete?: (documentId: string) => void;
  onDocumentDownload?: (documentId: string) => void;
  onRefresh?: () => void;
  isLoading?: boolean;
}

interface DocumentFilters {
  search: string;
  type: DocumentType | '';
  jurisdiction: Jurisdiction | '';
  status: AnalysisStatus | '';
}

export default function DocumentList({
  documents,
  onDocumentSelect,
  onDocumentDelete,
  onDocumentDownload,
  onRefresh,
  isLoading = false,
}: DocumentListProps) {
  const [filters, setFilters] = useState<DocumentFilters>({
    search: '',
    type: '',
    jurisdiction: '',
    status: '',
  });
  const [selectedDocuments, setSelectedDocuments] = useState<Set<string>>(new Set());
  const [showFilters, setShowFilters] = useState(false);

  // Filter documents based on current filters
  const filteredDocuments = useMemo(() => {
    return documents.filter((doc) => {
      const matchesSearch = !filters.search || 
        doc.name.toLowerCase().includes(filters.search.toLowerCase()) ||
        doc.metadata.parties.some(party => 
          party.toLowerCase().includes(filters.search.toLowerCase())
        );

      const matchesType = !filters.type || doc.type === filters.type;
      const matchesJurisdiction = !filters.jurisdiction || 
        doc.metadata.jurisdiction === filters.jurisdiction;
      const matchesStatus = !filters.status || doc.analysisStatus === filters.status;

      return matchesSearch && matchesType && matchesJurisdiction && matchesStatus;
    });
  }, [documents, filters]);

  const handleSelectDocument = (documentId: string) => {
    const newSelected = new Set(selectedDocuments);
    if (newSelected.has(documentId)) {
      newSelected.delete(documentId);
    } else {
      newSelected.add(documentId);
    }
    setSelectedDocuments(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedDocuments.size === filteredDocuments.length) {
      setSelectedDocuments(new Set());
    } else {
      setSelectedDocuments(new Set(filteredDocuments.map(doc => doc.id)));
    }
  };

  const getStatusIcon = (status: AnalysisStatus) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'processing':
        return <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: AnalysisStatus) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getAnalysisScore = (document: Document) => {
    if (!document.analysisResults?.complexity) return null;
    return document.analysisResults.complexity.overall;
  };

  return (
    <div className="space-y-4">
      {/* Search and Filters */}
      <div className="card">
        <div className="flex flex-col space-y-4">
          {/* Search Bar */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search documents, parties, or content..."
                value={filters.search}
                onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={cn(
                  'px-3 py-2 border rounded-md flex items-center transition-colors',
                  showFilters 
                    ? 'border-primary-300 bg-primary-50 text-primary-700'
                    : 'border-gray-300 hover:bg-gray-50'
                )}
              >
                <Filter className="w-4 h-4 mr-1" />
                Filters
              </button>
              {onRefresh && (
                <button
                  onClick={onRefresh}
                  disabled={isLoading}
                  className="px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 flex items-center disabled:opacity-50"
                  aria-label="Refresh documents"
                  title="Refresh documents"
                >
                  <RefreshCw className={cn('w-4 h-4', isLoading && 'animate-spin')} />
                </button>
              )}
            </div>
          </div>

          {/* Filter Controls */}
          {showFilters && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-gray-200">
              <div>
                <label htmlFor="document-type-filter" className="block text-sm font-medium text-gray-700 mb-1">
                  Document Type
                </label>
                <select
                  id="document-type-filter"
                  value={filters.type}
                  onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value as DocumentType }))}
                  className="input-field"
                >
                  <option value="">All Types</option>
                  <option value="contract">Contract</option>
                  <option value="agreement">Agreement</option>
                  <option value="mou">MOU</option>
                  <option value="nda">NDA</option>
                  <option value="invoice">Invoice</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label htmlFor="jurisdiction-filter" className="block text-sm font-medium text-gray-700 mb-1">
                  Jurisdiction
                </label>
                <select
                  id="jurisdiction-filter"
                  value={filters.jurisdiction}
                  onChange={(e) => setFilters(prev => ({ ...prev, jurisdiction: e.target.value as Jurisdiction }))}
                  className="input-field"
                >
                  <option value="">All Jurisdictions</option>
                  <option value="india">India</option>
                  <option value="usa">USA</option>
                  <option value="cross_border">Cross-border</option>
                  <option value="unknown">Unknown</option>
                </select>
              </div>

              <div>
                <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700 mb-1">
                  Analysis Status
                </label>
                <select
                  id="status-filter"
                  value={filters.status}
                  onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value as AnalysisStatus }))}
                  className="input-field"
                >
                  <option value="">All Statuses</option>
                  <option value="pending">Pending</option>
                  <option value="processing">Processing</option>
                  <option value="completed">Completed</option>
                  <option value="failed">Failed</option>
                </select>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Results Summary */}
      <div className="flex items-center justify-between text-sm text-gray-600">
        <span>
          Showing {filteredDocuments.length} of {documents.length} documents
        </span>
        {selectedDocuments.size > 0 && (
          <span>
            {selectedDocuments.size} selected
          </span>
        )}
      </div>

      {/* Documents Table */}
      <div className="card p-0">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedDocuments.size === filteredDocuments.length && filteredDocuments.length > 0}
                    onChange={handleSelectAll}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Document
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Jurisdiction
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Analysis Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Size
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Uploaded
                </th>
                <th className="relative px-6 py-3">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredDocuments.map((document) => {
                const analysisScore = getAnalysisScore(document);
                return (
                  <tr 
                    key={document.id} 
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => onDocumentSelect?.(document)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        checked={selectedDocuments.has(document.id)}
                        onChange={() => handleSelectDocument(document.id)}
                        className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <FileText className="w-5 h-5 text-gray-400 mr-3" />
                        <div>
                          <div className="text-sm font-medium text-gray-900 truncate max-w-xs">
                            {document.name}
                          </div>
                          {document.metadata.parties.length > 0 && (
                            <div className="text-xs text-gray-500 truncate max-w-xs">
                              Parties: {document.metadata.parties.join(', ')}
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="badge badge-secondary capitalize">
                        {document.type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {document.metadata.jurisdiction && (
                        <span className={cn(
                          'badge capitalize',
                          getJurisdictionColor(document.metadata.jurisdiction)
                        )}>
                          {document.metadata.jurisdiction.replace('_', ' ')}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {getStatusIcon(document.analysisStatus)}
                        <span className={cn(
                          'badge ml-2 capitalize',
                          getStatusColor(document.analysisStatus)
                        )}>
                          {document.analysisStatus}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {analysisScore ? (
                        <div className="flex items-center">
                          <span className="mr-2">{analysisScore}/100</span>
                          <div className="w-16 bg-gray-200 rounded-full h-2">
                            <div
                              className={cn(
                                'h-2 rounded-full',
                                analysisScore >= 80 ? 'bg-green-500' :
                                analysisScore >= 60 ? 'bg-yellow-500' :
                                'bg-red-500'
                              )}
                              style={{ width: `${analysisScore}%` }}
                            />
                          </div>
                        </div>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatFileSize(document.metadata.fileSize)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(document.uploadedAt)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center space-x-2" onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={() => onDocumentSelect?.(document)}
                          className="text-primary-600 hover:text-primary-900"
                          title="View Document"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => onDocumentDownload?.(document.id)}
                          className="text-gray-600 hover:text-gray-900"
                          title="Download"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => onDocumentDelete?.(document.id)}
                          className="text-red-600 hover:text-red-900"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          {/* Empty State */}
          {filteredDocuments.length === 0 && (
            <div className="text-center py-12">
              <FileText className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No documents found</h3>
              <p className="mt-1 text-sm text-gray-500">
                {documents.length === 0 
                  ? "Get started by uploading your first document."
                  : "Try adjusting your search or filter criteria."
                }
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}