'use client';

import React, { useState, useCallback } from 'react';
import { 
  ChevronUp, 
  ChevronDown, 
  SkipForward, 
  SkipBack,
  Play,
  Pause,
  RotateCcw
} from 'lucide-react';
import { DocumentDifference, ClauseSimilarity } from '@/types';

interface ComparisonNavigationProps {
  differences: DocumentDifference[];
  similarities: ClauseSimilarity[];
  currentIndex: number;
  onNavigate: (index: number) => void;
  onAutoNavigate?: (enabled: boolean) => void;
  onItemSelect?: (item: DocumentDifference | ClauseSimilarity) => void;
  autoNavigateInterval?: number;
  className?: string;
}

export const ComparisonNavigation: React.FC<ComparisonNavigationProps> = ({
  differences,
  similarities,
  currentIndex,
  onNavigate,
  onAutoNavigate,
  onItemSelect,
  autoNavigateInterval = 3000,
  className = ''
}) => {
  const [isAutoNavigating, setIsAutoNavigating] = useState<boolean>(false);
  const [showingType, setShowingType] = useState<'differences' | 'similarities'>('differences');

  const currentItems = showingType === 'differences' ? differences : similarities;
  const totalItems = currentItems.length;

  // Navigation functions
  const goToPrevious = useCallback(() => {
    if (currentIndex > 0) {
      const newIndex = currentIndex - 1;
      onNavigate(newIndex);
      onItemSelect?.(currentItems[newIndex]);
    }
  }, [currentIndex, onNavigate, onItemSelect, currentItems]);

  const goToNext = useCallback(() => {
    if (currentIndex < totalItems - 1) {
      const newIndex = currentIndex + 1;
      onNavigate(newIndex);
      onItemSelect?.(currentItems[newIndex]);
    }
  }, [currentIndex, totalItems, onNavigate, onItemSelect, currentItems]);

  const goToFirst = useCallback(() => {
    if (totalItems > 0) {
      onNavigate(0);
      onItemSelect?.(currentItems[0]);
    }
  }, [totalItems, onNavigate, onItemSelect, currentItems]);

  const goToLast = useCallback(() => {
    if (totalItems > 0) {
      const lastIndex = totalItems - 1;
      onNavigate(lastIndex);
      onItemSelect?.(currentItems[lastIndex]);
    }
  }, [totalItems, onNavigate, onItemSelect, currentItems]);

  // Auto-navigation toggle
  const toggleAutoNavigate = useCallback(() => {
    const newState = !isAutoNavigating;
    setIsAutoNavigating(newState);
    onAutoNavigate?.(newState);
  }, [isAutoNavigating, onAutoNavigate]);

  // Auto-navigation effect
  useEffect(() => {
    if (!isAutoNavigating || totalItems === 0) return;

    const interval = setInterval(() => {
      if (currentIndex < totalItems - 1) {
        goToNext();
      } else {
        // Auto-navigation reached the end, stop it
        setIsAutoNavigating(false);
        onAutoNavigate?.(false);
      }
    }, autoNavigateInterval);

    return () => clearInterval(interval);
  }, [isAutoNavigating, currentIndex, totalItems, autoNavigateInterval, goToNext, onAutoNavigate]);

  // Get current item info
  const getCurrentItemInfo = () => {
    if (totalItems === 0) return null;
    
    const currentItem = currentItems[currentIndex];
    if (!currentItem) return null;

    if (showingType === 'differences') {
      const diff = currentItem as DocumentDifference;
      return {
        title: `${diff.type.charAt(0).toUpperCase() + diff.type.slice(1)} - ${diff.category}`,
        description: diff.description,
        section: diff.section,
        severity: diff.severity
      };
    } else {
      const sim = currentItem as ClauseSimilarity;
      return {
        title: `${sim.type.charAt(0).toUpperCase() + sim.type.slice(1)} Clause`,
        description: sim.document1Clause.content.substring(0, 100) + '...',
        section: `${sim.document1Clause.section} ↔ ${sim.document2Clause.section}`,
        similarity: Math.round(sim.similarityScore * 100)
      };
    }
  };

  const currentItemInfo = getCurrentItemInfo();

  if (totalItems === 0) {
    return (
      <div className={`p-4 bg-gray-50 border border-gray-200 rounded-lg ${className}`}>
        <p className="text-sm text-gray-500 text-center">
          No {showingType} to navigate
        </p>
      </div>
    );
  }

  return (
    <div className={`bg-white border border-gray-200 rounded-lg shadow-sm ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <div className="flex bg-gray-100 rounded-md p-1">
            <button
              onClick={() => setShowingType('differences')}
              className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
                showingType === 'differences'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Differences ({differences.length})
            </button>
            <button
              onClick={() => setShowingType('similarities')}
              className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
                showingType === 'similarities'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Similarities ({similarities.length})
            </button>
          </div>
        </div>

        <div className="flex items-center space-x-1">
          {/* Auto-navigate toggle */}
          <button
            onClick={toggleAutoNavigate}
            className={`p-1.5 rounded transition-colors ${
              isAutoNavigating
                ? 'bg-blue-100 text-blue-600'
                : 'text-gray-400 hover:text-gray-600'
            }`}
            title={isAutoNavigating ? 'Stop auto-navigation' : 'Start auto-navigation'}
          >
            {isAutoNavigating ? (
              <Pause className="w-4 h-4" />
            ) : (
              <Play className="w-4 h-4" />
            )}
          </button>

          {/* Reset to first */}
          <button
            onClick={goToFirst}
            disabled={currentIndex === 0}
            className="p-1.5 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Go to first"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Navigation Controls */}
      <div className="flex items-center justify-between p-3 border-b border-gray-200">
        <div className="flex items-center space-x-1">
          <button
            onClick={goToFirst}
            disabled={currentIndex === 0}
            className="p-1.5 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
            title="First item"
          >
            <SkipBack className="w-4 h-4" />
          </button>
          
          <button
            onClick={goToPrevious}
            disabled={currentIndex === 0}
            className="p-1.5 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Previous item"
          >
            <ChevronUp className="w-4 h-4" />
          </button>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">
            {currentIndex + 1} of {totalItems}
          </span>
          <div className="w-24 bg-gray-200 rounded-full h-1.5">
            <div
              className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
              style={{ width: `${((currentIndex + 1) / totalItems) * 100}%` }}
            />
          </div>
        </div>

        <div className="flex items-center space-x-1">
          <button
            onClick={goToNext}
            disabled={currentIndex >= totalItems - 1}
            className="p-1.5 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Next item"
          >
            <ChevronDown className="w-4 h-4" />
          </button>
          
          <button
            onClick={goToLast}
            disabled={currentIndex >= totalItems - 1}
            className="p-1.5 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Last item"
          >
            <SkipForward className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Current Item Info */}
      {currentItemInfo && (
        <div className="p-3">
          <div className="flex items-start justify-between mb-2">
            <h4 className="text-sm font-medium text-gray-900">
              {currentItemInfo.title}
            </h4>
            {showingType === 'differences' && currentItemInfo.severity && (
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                currentItemInfo.severity === 'high' 
                  ? 'bg-red-100 text-red-800'
                  : currentItemInfo.severity === 'medium'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-green-100 text-green-800'
              }`}>
                {currentItemInfo.severity}
              </span>
            )}
            {showingType === 'similarities' && currentItemInfo.similarity && (
              <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                {currentItemInfo.similarity}%
              </span>
            )}
          </div>
          
          <p className="text-sm text-gray-600 mb-2 line-clamp-2">
            {currentItemInfo.description}
          </p>
          
          <p className="text-xs text-gray-500">
            Section: {currentItemInfo.section}
          </p>
        </div>
      )}

      {/* Quick Jump */}
      <div className="p-3 border-t border-gray-200">
        <div className="flex items-center space-x-2">
          <label className="text-xs text-gray-600">Jump to:</label>
          <input
            type="number"
            min={1}
            max={totalItems}
            value={currentIndex + 1}
            onChange={(e) => {
              const index = parseInt(e.target.value) - 1;
              if (index >= 0 && index < totalItems) {
                onNavigate(index);
              }
            }}
            className="w-16 px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
          <span className="text-xs text-gray-500">of {totalItems}</span>
        </div>
      </div>
    </div>
  );
};

export default ComparisonNavigation;