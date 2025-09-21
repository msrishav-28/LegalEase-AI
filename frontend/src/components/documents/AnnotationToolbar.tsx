'use client';

import React, { useState, useCallback } from 'react';
import { 
  MessageSquare, 
  Highlighter, 
  Type, 
  Square,
  Circle,
  ArrowRight,
  Trash2,
  Save,
  X
} from 'lucide-react';

export type AnnotationType = 'highlight' | 'comment' | 'text' | 'rectangle' | 'circle' | 'arrow';

interface AnnotationToolbarProps {
  selectedTool: AnnotationType | null;
  onToolSelect: (tool: AnnotationType | null) => void;
  onSaveAnnotation?: () => void;
  onDeleteAnnotation?: () => void;
  hasActiveAnnotation?: boolean;
  className?: string;
}

interface AnnotationTool {
  type: AnnotationType;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  shortcut?: string;
}

const annotationTools: AnnotationTool[] = [
  {
    type: 'highlight',
    icon: Highlighter,
    label: 'Highlight Text',
    shortcut: 'H'
  },
  {
    type: 'comment',
    icon: MessageSquare,
    label: 'Add Comment',
    shortcut: 'C'
  },
  {
    type: 'text',
    icon: Type,
    label: 'Add Text',
    shortcut: 'T'
  },
  {
    type: 'rectangle',
    icon: Square,
    label: 'Rectangle',
    shortcut: 'R'
  },
  {
    type: 'circle',
    icon: Circle,
    label: 'Circle',
    shortcut: 'O'
  },
  {
    type: 'arrow',
    icon: ArrowRight,
    label: 'Arrow',
    shortcut: 'A'
  }
];

export const AnnotationToolbar: React.FC<AnnotationToolbarProps> = ({
  selectedTool,
  onToolSelect,
  onSaveAnnotation,
  onDeleteAnnotation,
  hasActiveAnnotation = false,
  className = ''
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleToolClick = useCallback((tool: AnnotationType) => {
    if (selectedTool === tool) {
      onToolSelect(null);
    } else {
      onToolSelect(tool);
    }
  }, [selectedTool, onToolSelect]);

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (event.altKey) {
      const tool = annotationTools.find(t => 
        t.shortcut?.toLowerCase() === event.key.toLowerCase()
      );
      if (tool) {
        event.preventDefault();
        handleToolClick(tool.type);
      }
    }
    
    if (event.key === 'Escape') {
      onToolSelect(null);
    }
  }, [handleToolClick, onToolSelect]);

  React.useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return (
    <div className={`bg-white border border-gray-200 rounded-lg shadow-sm ${className}`}>
      {/* Main toolbar */}
      <div className="flex items-center p-2 space-x-1">
        {/* Tool buttons */}
        {annotationTools.map((tool) => {
          const Icon = tool.icon;
          const isSelected = selectedTool === tool.type;
          
          return (
            <button
              key={tool.type}
              onClick={() => handleToolClick(tool.type)}
              className={`
                p-2 rounded-md transition-colors duration-200
                ${isSelected 
                  ? 'bg-blue-100 text-blue-700 border border-blue-300' 
                  : 'hover:bg-gray-100 text-gray-600'
                }
              `}
              title={`${tool.label} (Alt+${tool.shortcut})`}
            >
              <Icon className="w-4 h-4" />
            </button>
          );
        })}

        {/* Divider */}
        <div className="w-px h-6 bg-gray-300 mx-2" />

        {/* Action buttons */}
        {hasActiveAnnotation && (
          <>
            <button
              onClick={onSaveAnnotation}
              className="p-2 rounded-md hover:bg-green-100 text-green-600 transition-colors duration-200"
              title="Save Annotation (Ctrl+S)"
            >
              <Save className="w-4 h-4" />
            </button>
            
            <button
              onClick={onDeleteAnnotation}
              className="p-2 rounded-md hover:bg-red-100 text-red-600 transition-colors duration-200"
              title="Delete Annotation (Delete)"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </>
        )}

        {/* Clear selection */}
        {selectedTool && (
          <button
            onClick={() => onToolSelect(null)}
            className="p-2 rounded-md hover:bg-gray-100 text-gray-600 transition-colors duration-200"
            title="Clear Selection (Esc)"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Tool info */}
      {selectedTool && (
        <div className="px-3 py-2 bg-gray-50 border-t border-gray-200 text-sm text-gray-600">
          {selectedTool === 'highlight' && (
            <span>Select text to highlight it</span>
          )}
          {selectedTool === 'comment' && (
            <span>Click on the document to add a comment</span>
          )}
          {selectedTool === 'text' && (
            <span>Click on the document to add text</span>
          )}
          {(selectedTool === 'rectangle' || selectedTool === 'circle') && (
            <span>Click and drag to draw a {selectedTool}</span>
          )}
          {selectedTool === 'arrow' && (
            <span>Click and drag to draw an arrow</span>
          )}
        </div>
      )}
    </div>
  );
};

export default AnnotationToolbar;