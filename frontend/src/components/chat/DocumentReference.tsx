import React from 'react';
import { clsx } from 'clsx';
import { ExternalLink, FileText, MapPin } from 'lucide-react';
import { DocumentReference as DocumentReferenceType } from '@/types';
import JurisdictionBadge from './JurisdictionBadge';

interface DocumentReferenceProps {
  reference: DocumentReferenceType;
  onClick?: (reference: DocumentReferenceType) => void;
  className?: string;
}

const getJurisdictionBadge = (jurisdiction?: string) => {
  switch (jurisdiction) {
    case 'india':
      return { jurisdiction: 'india' as const, confidence: 1, color: 'orange' as const, label: 'India' };
    case 'usa':
      return { jurisdiction: 'usa' as const, confidence: 1, color: 'blue' as const, label: 'USA' };
    case 'cross_border':
      return { jurisdiction: 'cross_border' as const, confidence: 1, color: 'purple' as const, label: 'Cross-Border' };
    default:
      return null;
  }
};

export default function DocumentReference({
  reference,
  onClick,
  className
}: DocumentReferenceProps) {
  const jurisdictionBadge = getJurisdictionBadge(reference.jurisdiction);
  const relevancePercentage = Math.round(reference.relevance * 100);

  const handleClick = () => {
    if (onClick) {
      onClick(reference);
    }
  };

  return (
    <div
      className={clsx(
        'group border rounded-lg p-3 hover:bg-gray-50 transition-colors cursor-pointer',
        'border-gray-200 hover:border-gray-300',
        className
      )}
      onClick={handleClick}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center space-x-2 min-w-0 flex-1">
          <FileText className="h-4 w-4 text-gray-500 flex-shrink-0" />
          <span className="font-medium text-gray-900 truncate">
            {reference.documentName}
          </span>
          <ExternalLink className="h-3 w-3 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
        <div className="flex items-center space-x-2 flex-shrink-0 ml-2">
          {jurisdictionBadge && (
            <JurisdictionBadge badge={jurisdictionBadge} size="sm" showConfidence={false} />
          )}
          <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
            {relevancePercentage}% match
          </span>
        </div>
      </div>

      {(reference.section || reference.pageNumber) && (
        <div className="flex items-center space-x-3 mb-2 text-sm text-gray-600">
          {reference.section && (
            <div className="flex items-center space-x-1">
              <MapPin className="h-3 w-3" />
              <span>Section: {reference.section}</span>
            </div>
          )}
          {reference.pageNumber && (
            <span>Page {reference.pageNumber}</span>
          )}
        </div>
      )}

      <p className="text-sm text-gray-700 line-clamp-2">
        {reference.excerpt}
      </p>
    </div>
  );
}