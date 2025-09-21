import React from 'react';
import { clsx } from 'clsx';
import { 
  MessageSquare, 
  Command, 
  Scale, 
  Globe,
  ChevronRight 
} from 'lucide-react';
import { ChatSuggestion } from '@/types';
import JurisdictionBadge from './JurisdictionBadge';

interface ChatAutoCompleteProps {
  suggestions: ChatSuggestion[];
  onSelect: (suggestion: ChatSuggestion) => void;
  isVisible: boolean;
  className?: string;
}

const getIconForType = (type: string) => {
  switch (type) {
    case 'question':
      return MessageSquare;
    case 'command':
      return Command;
    case 'legal_term':
      return Scale;
    case 'jurisdiction_specific':
      return Globe;
    default:
      return MessageSquare;
  }
};

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

export default function ChatAutoComplete({
  suggestions,
  onSelect,
  isVisible,
  className
}: ChatAutoCompleteProps) {
  if (!isVisible || suggestions.length === 0) {
    return null;
  }

  return (
    <div className={clsx(
      'absolute bottom-full left-0 right-0 mb-2 bg-white border border-gray-200 rounded-lg shadow-lg max-h-64 overflow-y-auto z-50',
      className
    )}>
      <div className="p-2">
        <div className="text-xs font-medium text-gray-500 mb-2 px-2">
          Jurisdiction-aware suggestions
        </div>
        
        {suggestions.map((suggestion, index) => {
          const Icon = getIconForType(suggestion.type);
          const jurisdictionBadge = getJurisdictionBadge(suggestion.jurisdiction);
          
          return (
            <button
              key={index}
              onClick={() => onSelect(suggestion)}
              className="w-full text-left p-2 rounded-md hover:bg-gray-50 transition-colors group"
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-0.5">
                  <Icon className="h-4 w-4 text-gray-400 group-hover:text-gray-600" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-900 truncate">
                      {suggestion.text}
                    </span>
                    <div className="flex items-center space-x-2 flex-shrink-0 ml-2">
                      {jurisdictionBadge && (
                        <JurisdictionBadge 
                          badge={jurisdictionBadge} 
                          size="sm" 
                          showConfidence={false} 
                        />
                      )}
                      <ChevronRight className="h-3 w-3 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                      {suggestion.category}
                    </span>
                    {suggestion.description && (
                      <span className="text-xs text-gray-500 truncate">
                        {suggestion.description}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}