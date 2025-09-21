import React, { useState, useRef, useCallback, useEffect } from 'react';
import { clsx } from 'clsx';
import { Send, Paperclip, Mic, MicOff } from 'lucide-react';
import { ChatSuggestion, Jurisdiction } from '@/types';
import ChatAutoComplete from './ChatAutoComplete';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  onTyping?: (isTyping: boolean) => void;
  jurisdiction?: Jurisdiction;
  disabled?: boolean;
  placeholder?: string;
  className?: string;
}

// Mock jurisdiction-specific suggestions
const getJurisdictionSuggestions = (input: string, jurisdiction?: Jurisdiction): ChatSuggestion[] => {
  const commonSuggestions: ChatSuggestion[] = [
    {
      text: "What are the key risks in this document?",
      type: 'question',
      category: 'Risk Analysis',
      description: 'Analyze potential legal risks'
    },
    {
      text: "Summarize the main obligations",
      type: 'question', 
      category: 'Obligations',
      description: 'Extract key obligations and duties'
    },
    {
      text: "What are the termination clauses?",
      type: 'question',
      category: 'Contract Terms',
      description: 'Find termination and exit provisions'
    }
  ];

  const indianSuggestions: ChatSuggestion[] = [
    {
      text: "What is the stamp duty requirement?",
      type: 'jurisdiction_specific',
      jurisdiction: 'india',
      category: 'Indian Law',
      description: 'Calculate stamp duty obligations'
    },
    {
      text: "Check GST implications",
      type: 'jurisdiction_specific',
      jurisdiction: 'india',
      category: 'Tax Law',
      description: 'Analyze GST applicability'
    },
    {
      text: "Verify Indian Contract Act compliance",
      type: 'jurisdiction_specific',
      jurisdiction: 'india',
      category: 'Compliance',
      description: 'Check ICA 1872 compliance'
    },
    {
      text: "What registration is required?",
      type: 'jurisdiction_specific',
      jurisdiction: 'india',
      category: 'Registration',
      description: 'Document registration requirements'
    }
  ];

  const usSuggestions: ChatSuggestion[] = [
    {
      text: "Check UCC applicability",
      type: 'jurisdiction_specific',
      jurisdiction: 'usa',
      category: 'US Law',
      description: 'Uniform Commercial Code analysis'
    },
    {
      text: "Analyze choice of law provisions",
      type: 'jurisdiction_specific',
      jurisdiction: 'usa',
      category: 'Jurisdiction',
      description: 'Governing law analysis'
    },
    {
      text: "Review securities law compliance",
      type: 'jurisdiction_specific',
      jurisdiction: 'usa',
      category: 'Securities',
      description: 'SEC compliance check'
    },
    {
      text: "Check CCPA privacy requirements",
      type: 'jurisdiction_specific',
      jurisdiction: 'usa',
      category: 'Privacy',
      description: 'California privacy law compliance'
    }
  ];

  const crossBorderSuggestions: ChatSuggestion[] = [
    {
      text: "Compare enforceability across jurisdictions",
      type: 'jurisdiction_specific',
      jurisdiction: 'cross_border',
      category: 'Cross-Border',
      description: 'Multi-jurisdiction enforceability'
    },
    {
      text: "Analyze tax treaty implications",
      type: 'jurisdiction_specific',
      jurisdiction: 'cross_border',
      category: 'Tax Treaties',
      description: 'India-US DTAA considerations'
    },
    {
      text: "Review dispute resolution mechanisms",
      type: 'jurisdiction_specific',
      jurisdiction: 'cross_border',
      category: 'Disputes',
      description: 'International arbitration options'
    }
  ];

  let suggestions = [...commonSuggestions];

  if (jurisdiction === 'india') {
    suggestions = [...suggestions, ...indianSuggestions];
  } else if (jurisdiction === 'usa') {
    suggestions = [...suggestions, ...usSuggestions];
  } else if (jurisdiction === 'cross_border') {
    suggestions = [...suggestions, ...crossBorderSuggestions];
  }

  // Filter suggestions based on input
  if (input.trim()) {
    suggestions = suggestions.filter(s => 
      s.text.toLowerCase().includes(input.toLowerCase()) ||
      s.category.toLowerCase().includes(input.toLowerCase()) ||
      (s.description && s.description.toLowerCase().includes(input.toLowerCase()))
    );
  }

  return suggestions.slice(0, 6); // Limit to 6 suggestions
};

export default function ChatInput({
  onSendMessage,
  onTyping,
  jurisdiction,
  disabled = false,
  placeholder = "Ask about this document...",
  className
}: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [suggestions, setSuggestions] = useState<ChatSuggestion[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout>();

  // Auto-resize textarea
  const adjustTextareaHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  }, []);

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setMessage(value);
    adjustTextareaHeight();

    // Update suggestions
    const newSuggestions = getJurisdictionSuggestions(value, jurisdiction);
    setSuggestions(newSuggestions);
    setShowSuggestions(value.length > 0 && newSuggestions.length > 0);

    // Handle typing indicator
    if (onTyping) {
      onTyping(true);
      
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      
      typingTimeoutRef.current = setTimeout(() => {
        onTyping(false);
      }, 1000);
    }
  };

  // Handle send message
  const handleSendMessage = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
      setShowSuggestions(false);
      setSuggestions([]);
      
      if (onTyping) {
        onTyping(false);
      }
      
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  // Handle key press
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Handle suggestion selection
  const handleSuggestionSelect = (suggestion: ChatSuggestion) => {
    setMessage(suggestion.text);
    setShowSuggestions(false);
    setSuggestions([]);
    
    // Focus textarea and adjust height
    if (textareaRef.current) {
      textareaRef.current.focus();
      setTimeout(adjustTextareaHeight, 0);
    }
  };

  // Handle voice recording (placeholder)
  const handleVoiceToggle = () => {
    setIsRecording(!isRecording);
    // TODO: Implement voice recording functionality
  };

  // Handle file attachment (placeholder)
  const handleFileAttach = () => {
    // TODO: Implement file attachment functionality
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, []);

  return (
    <div className={clsx('relative', className)}>
      {/* Auto-complete suggestions */}
      <ChatAutoComplete
        suggestions={suggestions}
        onSelect={handleSuggestionSelect}
        isVisible={showSuggestions}
      />

      {/* Input container */}
      <div className="flex items-end space-x-2 p-4 border-t border-gray-200 bg-white">
        {/* Attachment button */}
        <button
          onClick={handleFileAttach}
          disabled={disabled}
          className="flex-shrink-0 p-2 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title="Attach file"
        >
          <Paperclip className="h-5 w-5" />
        </button>

        {/* Message input */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className={clsx(
              'w-full resize-none rounded-lg border border-gray-300 px-4 py-3 pr-12',
              'focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none',
              'disabled:bg-gray-50 disabled:cursor-not-allowed',
              'placeholder-gray-500 text-sm'
            )}
            style={{ minHeight: '44px', maxHeight: '120px' }}
          />
          
          {/* Jurisdiction indicator */}
          {jurisdiction && (
            <div className="absolute top-2 right-12">
              <span className={clsx(
                'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                jurisdiction === 'india' && 'bg-orange-100 text-orange-800',
                jurisdiction === 'usa' && 'bg-blue-100 text-blue-800',
                jurisdiction === 'cross_border' && 'bg-purple-100 text-purple-800',
                !['india', 'usa', 'cross_border'].includes(jurisdiction) && 'bg-gray-100 text-gray-800'
              )}>
                {jurisdiction === 'india' ? 'IN' : 
                 jurisdiction === 'usa' ? 'US' : 
                 jurisdiction === 'cross_border' ? 'CB' : 
                 jurisdiction.toUpperCase()}
              </span>
            </div>
          )}
        </div>

        {/* Voice recording button */}
        <button
          onClick={handleVoiceToggle}
          disabled={disabled}
          className={clsx(
            'flex-shrink-0 p-2 transition-colors',
            isRecording 
              ? 'text-red-600 hover:text-red-700' 
              : 'text-gray-400 hover:text-gray-600',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
          title={isRecording ? 'Stop recording' : 'Start voice recording'}
        >
          {isRecording ? (
            <MicOff className="h-5 w-5" />
          ) : (
            <Mic className="h-5 w-5" />
          )}
        </button>

        {/* Send button */}
        <button
          onClick={handleSendMessage}
          disabled={disabled || !message.trim()}
          className={clsx(
            'flex-shrink-0 p-2 rounded-lg transition-colors',
            message.trim() && !disabled
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
          )}
          title="Send message"
        >
          <Send className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
}