import React from 'react';
import { clsx } from 'clsx';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { 
  User, 
  Bot, 
  Clock, 
  AlertCircle, 
  CheckCircle,
  Loader2
} from 'lucide-react';
import { ChatMessage as ChatMessageType } from '@/types';
import JurisdictionBadge from './JurisdictionBadge';
import DocumentReference from './DocumentReference';

interface ChatMessageProps {
  message: ChatMessageType;
  onReferenceClick?: (reference: any) => void;
  className?: string;
}

const getStatusIcon = (status?: string) => {
  switch (status) {
    case 'sending':
      return <Loader2 className="h-3 w-3 animate-spin text-gray-400" />;
    case 'sent':
      return <CheckCircle className="h-3 w-3 text-green-500" />;
    case 'error':
      return <AlertCircle className="h-3 w-3 text-red-500" />;
    default:
      return null;
  }
};

const getJurisdictionBadge = (jurisdiction?: string, confidence?: number) => {
  if (!jurisdiction) return null;
  
  switch (jurisdiction) {
    case 'india':
      return { 
        jurisdiction: 'india' as const, 
        confidence: confidence || 1, 
        color: 'orange' as const, 
        label: 'India' 
      };
    case 'usa':
      return { 
        jurisdiction: 'usa' as const, 
        confidence: confidence || 1, 
        color: 'blue' as const, 
        label: 'USA' 
      };
    case 'cross_border':
      return { 
        jurisdiction: 'cross_border' as const, 
        confidence: confidence || 1, 
        color: 'purple' as const, 
        label: 'Cross-Border' 
      };
    default:
      return null;
  }
};

export default function ChatMessage({
  message,
  onReferenceClick,
  className
}: ChatMessageProps) {
  const isUser = message.role === 'user';
  const jurisdictionBadge = message.jurisdictionBadge || 
    getJurisdictionBadge(message.jurisdiction, message.confidence);
  const statusIcon = getStatusIcon(message.status);

  return (
    <div className={clsx(
      'flex items-start space-x-3 p-4',
      isUser ? 'flex-row-reverse space-x-reverse' : '',
      className
    )}>
      {/* Avatar */}
      <div className="flex-shrink-0">
        <div className={clsx(
          'w-8 h-8 rounded-full flex items-center justify-center',
          isUser ? 'bg-blue-600' : 'bg-gray-100'
        )}>
          {isUser ? (
            <User className="h-4 w-4 text-white" />
          ) : (
            <Bot className="h-4 w-4 text-gray-600" />
          )}
        </div>
      </div>

      {/* Message Content */}
      <div className={clsx(
        'flex-1 min-w-0',
        isUser ? 'text-right' : 'text-left'
      )}>
        {/* Message Header */}
        <div className={clsx(
          'flex items-center space-x-2 mb-1',
          isUser ? 'justify-end' : 'justify-start'
        )}>
          <span className="text-sm font-medium text-gray-900">
            {isUser ? 'You' : 'LegalEase AI'}
          </span>
          
          {jurisdictionBadge && (
            <JurisdictionBadge badge={jurisdictionBadge} size="sm" />
          )}
          
          <div className="flex items-center space-x-1 text-xs text-gray-500">
            <Clock className="h-3 w-3" />
            <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
            {statusIcon}
          </div>
        </div>

        {/* Message Body */}
        <div className={clsx(
          'rounded-lg px-4 py-3 max-w-3xl',
          isUser 
            ? 'bg-blue-600 text-white ml-auto' 
            : 'bg-gray-100 text-gray-900'
        )}>
          {isUser ? (
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  // Customize markdown rendering for better styling
                  p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                  ul: ({ children }) => <ul className="mb-2 pl-4 list-disc">{children}</ul>,
                  ol: ({ children }) => <ol className="mb-2 pl-4 list-decimal">{children}</ol>,
                  li: ({ children }) => <li className="mb-1">{children}</li>,
                  code: ({ children }) => (
                    <code className="bg-gray-200 px-1 py-0.5 rounded text-xs font-mono">
                      {children}
                    </code>
                  ),
                  pre: ({ children }) => (
                    <pre className="bg-gray-200 p-2 rounded text-xs overflow-x-auto">
                      {children}
                    </pre>
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Confidence Score */}
        {!isUser && message.confidence && (
          <div className="mt-2 text-xs text-gray-500">
            Confidence: {Math.round(message.confidence * 100)}%
          </div>
        )}

        {/* Document References */}
        {!isUser && message.references && message.references.length > 0 && (
          <div className="mt-3 space-y-2">
            <div className="text-xs font-medium text-gray-700">
              Referenced Documents:
            </div>
            {message.references.map((reference, index) => (
              <DocumentReference
                key={index}
                reference={reference}
                onClick={onReferenceClick}
                className="text-sm"
              />
            ))}
          </div>
        )}

        {/* Metadata */}
        {!isUser && message.metadata && (
          <div className="mt-2 text-xs text-gray-500 space-y-1">
            {message.metadata.processingTime && (
              <div>Processing time: {message.metadata.processingTime}ms</div>
            )}
            {message.metadata.jurisdictionContext && (
              <div className="space-y-1">
                <div>Jurisdiction context:</div>
                <div className="pl-2 space-y-0.5">
                  {message.metadata.jurisdictionContext.applicableLaws.length > 0 && (
                    <div>Laws: {message.metadata.jurisdictionContext.applicableLaws.join(', ')}</div>
                  )}
                  {message.metadata.jurisdictionContext.complianceRequirements && 
                   message.metadata.jurisdictionContext.complianceRequirements.length > 0 && (
                    <div>Compliance: {message.metadata.jurisdictionContext.complianceRequirements.join(', ')}</div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}