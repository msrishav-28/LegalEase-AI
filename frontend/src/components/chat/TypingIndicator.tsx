import React from 'react';
import { clsx } from 'clsx';
import { Bot } from 'lucide-react';
import { TypingIndicator as TypingIndicatorType } from '@/types';
import JurisdictionBadge from './JurisdictionBadge';

interface TypingIndicatorProps {
  indicator: TypingIndicatorType;
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

export default function TypingIndicator({
  indicator,
  className
}: TypingIndicatorProps) {
  const jurisdictionBadge = getJurisdictionBadge(indicator.jurisdiction);

  if (!indicator.isTyping) {
    return null;
  }

  return (
    <div className={clsx('flex items-start space-x-3 p-4', className)}>
      <div className="flex-shrink-0">
        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
          <Bot className="h-4 w-4 text-blue-600" />
        </div>
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center space-x-2 mb-1">
          <span className="text-sm font-medium text-gray-900">
            {indicator.userName}
          </span>
          {jurisdictionBadge && (
            <JurisdictionBadge badge={jurisdictionBadge} size="sm" showConfidence={false} />
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <span className="text-xs text-gray-500">typing...</span>
        </div>
      </div>
    </div>
  );
}