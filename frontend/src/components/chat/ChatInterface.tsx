import React, { useState, useEffect, useRef, useCallback } from 'react';
import { clsx } from 'clsx';
import { 
  MessageSquare, 
  Settings, 
  Maximize2, 
  Minimize2,
  RefreshCw,
  AlertCircle
} from 'lucide-react';
import { 
  ChatMessage as ChatMessageType, 
  ChatSession, 
  Jurisdiction,
  Document,
  TypingIndicator as TypingIndicatorType
} from '@/types';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import ChatHistory from './ChatHistory';
import TypingIndicator from './TypingIndicator';

interface ChatInterfaceProps {
  document?: Document;
  jurisdiction?: Jurisdiction;
  onDocumentReferenceClick?: (reference: any) => void;
  className?: string;
}

// Mock data for development
const mockSessions: ChatSession[] = [
  {
    id: '1',
    documentId: 'doc1',
    title: 'Contract Analysis - Service Agreement',
    jurisdiction: 'india',
    messages: [
      {
        id: '1',
        content: 'What are the key risks in this service agreement?',
        role: 'user',
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        jurisdiction: 'india'
      },
      {
        id: '2',
        content: 'Based on my analysis of this Indian service agreement, I\'ve identified several key risks:\n\n## High Priority Risks\n\n1. **Stamp Duty Non-compliance** - The agreement may require stamp duty payment in the state of execution\n2. **Liability Cap Issues** - The liability limitation clause may not be enforceable under Indian Contract Act\n3. **Termination Notice Period** - 30-day notice may be insufficient for certain service types\n\n## Medium Priority Risks\n\n1. **GST Implications** - Service tax obligations need clarification\n2. **Data Protection** - DPDP Act compliance requirements missing\n\nWould you like me to elaborate on any of these risks?',
        role: 'assistant',
        timestamp: new Date(Date.now() - 3590000).toISOString(),
        jurisdiction: 'india',
        confidence: 0.92,
        references: [
          {
            documentId: 'doc1',
            documentName: 'Service Agreement.pdf',
            section: 'Clause 8 - Liability',
            pageNumber: 3,
            relevance: 0.95,
            excerpt: 'The Service Provider\'s liability shall be limited to the amount paid...',
            jurisdiction: 'india'
          }
        ]
      }
    ],
    createdAt: new Date(Date.now() - 3600000).toISOString(),
    updatedAt: new Date(Date.now() - 3590000).toISOString(),
    isActive: true
  },
  {
    id: '2',
    documentId: 'doc2',
    title: 'Cross-Border M&A Agreement',
    jurisdiction: 'cross_border',
    messages: [
      {
        id: '3',
        content: 'Compare the enforceability of this agreement in India vs USA',
        role: 'user',
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        jurisdiction: 'cross_border'
      }
    ],
    createdAt: new Date(Date.now() - 7200000).toISOString(),
    updatedAt: new Date(Date.now() - 7200000).toISOString(),
    isActive: false
  }
];

export default function ChatInterface({
  document,
  jurisdiction,
  onDocumentReferenceClick,
  className
}: ChatInterfaceProps) {
  const [sessions, setSessions] = useState<ChatSession[]>(mockSessions);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(sessions[0] || null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [typingIndicator, setTypingIndicator] = useState<TypingIndicatorType | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [currentSession?.messages, scrollToBottom]);

  // Handle sending a new message
  const handleSendMessage = useCallback(async (content: string) => {
    if (!currentSession) {
      // Create new session if none exists
      const newSession: ChatSession = {
        id: Date.now().toString(),
        documentId: document?.id,
        title: `Chat ${Date.now()}`,
        jurisdiction: jurisdiction || document?.metadata.jurisdiction,
        messages: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        isActive: true
      };
      setCurrentSession(newSession);
      setSessions(prev => [newSession, ...prev]);
    }

    const userMessage: ChatMessageType = {
      id: Date.now().toString(),
      content,
      role: 'user',
      timestamp: new Date().toISOString(),
      jurisdiction: jurisdiction || document?.metadata.jurisdiction,
      status: 'sending'
    };

    // Add user message
    const updatedSession = {
      ...currentSession!,
      messages: [...(currentSession?.messages || []), userMessage],
      updatedAt: new Date().toISOString()
    };
    
    setCurrentSession(updatedSession);
    setSessions(prev => prev.map(s => s.id === updatedSession.id ? updatedSession : s));

    // Show typing indicator
    setTypingIndicator({
      userId: 'ai',
      userName: 'LegalEase AI',
      isTyping: true,
      jurisdiction: jurisdiction || document?.metadata.jurisdiction
    });

    setIsLoading(true);
    setError(null);

    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Mock AI response
      const aiResponse: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        content: `I understand you're asking about "${content}". Based on the ${jurisdiction || 'current'} jurisdiction context, here's my analysis:\n\n**Key Points:**\n- This appears to be a ${document?.type || 'legal'} document\n- Jurisdiction-specific considerations apply\n- Compliance requirements need review\n\nWould you like me to provide more specific analysis on any particular aspect?`,
        role: 'assistant',
        timestamp: new Date().toISOString(),
        jurisdiction: jurisdiction || document?.metadata.jurisdiction,
        confidence: 0.87,
        status: 'sent',
        metadata: {
          processingTime: 1850,
          modelUsed: 'gpt-4',
          jurisdictionContext: {
            detectedJurisdiction: jurisdiction || document?.metadata.jurisdiction || 'unknown',
            confidence: 0.92,
            applicableLaws: ['Contract Law', 'Commercial Law'],
            complianceRequirements: ['Document Registration', 'Stamp Duty']
          }
        }
      };

      // Update user message status
      const finalSession = {
        ...updatedSession,
        messages: [
          ...updatedSession.messages.slice(0, -1),
          { ...userMessage, status: 'sent' as const },
          aiResponse
        ],
        updatedAt: new Date().toISOString()
      };

      setCurrentSession(finalSession);
      setSessions(prev => prev.map(s => s.id === finalSession.id ? finalSession : s));

    } catch (err) {
      setError('Failed to send message. Please try again.');
      
      // Update user message status to error
      const errorSession = {
        ...updatedSession,
        messages: [
          ...updatedSession.messages.slice(0, -1),
          { ...userMessage, status: 'error' as const }
        ]
      };
      
      setCurrentSession(errorSession);
      setSessions(prev => prev.map(s => s.id === errorSession.id ? errorSession : s));
    } finally {
      setIsLoading(false);
      setTypingIndicator(null);
    }
  }, [currentSession, document, jurisdiction]);

  // Handle typing indicator
  const handleTyping = useCallback((isTyping: boolean) => {
    // This would typically send typing status to other users via WebSocket
    console.log('User typing:', isTyping);
  }, []);

  // Handle session selection
  const handleSessionSelect = useCallback((session: ChatSession) => {
    setCurrentSession(session);
    setShowHistory(false);
  }, []);

  // Handle session deletion
  const handleSessionDelete = useCallback((sessionId: string) => {
    setSessions(prev => prev.filter(s => s.id !== sessionId));
    if (currentSession?.id === sessionId) {
      setCurrentSession(sessions.find(s => s.id !== sessionId) || null);
    }
  }, [currentSession, sessions]);

  // Handle new session creation
  const handleNewSession = useCallback(() => {
    const newSession: ChatSession = {
      id: Date.now().toString(),
      documentId: document?.id,
      title: `New Chat ${new Date().toLocaleTimeString()}`,
      jurisdiction: jurisdiction || document?.metadata.jurisdiction,
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      isActive: true
    };
    
    setCurrentSession(newSession);
    setSessions(prev => [newSession, ...prev]);
    setShowHistory(false);
  }, [document, jurisdiction]);

  // Handle retry failed message
  const handleRetryMessage = useCallback(() => {
    if (currentSession) {
      const lastMessage = currentSession.messages[currentSession.messages.length - 1];
      if (lastMessage && lastMessage.role === 'user' && lastMessage.status === 'error') {
        handleSendMessage(lastMessage.content);
      }
    }
  }, [currentSession, handleSendMessage]);

  return (
    <div className={clsx(
      'flex flex-col bg-white border border-gray-200 rounded-lg shadow-sm',
      isExpanded ? 'fixed inset-4 z-50' : 'h-96',
      className
    )}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50 rounded-t-lg">
        <div className="flex items-center space-x-3">
          <MessageSquare className="h-5 w-5 text-blue-600" />
          <div>
            <h3 className="text-sm font-semibold text-gray-900">
              LegalEase AI Chat
            </h3>
            {document && (
              <p className="text-xs text-gray-600">
                Analyzing: {document.name}
              </p>
            )}
          </div>
          {jurisdiction && (
            <span className={clsx(
              'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
              jurisdiction === 'india' && 'bg-orange-100 text-orange-800',
              jurisdiction === 'usa' && 'bg-blue-100 text-blue-800',
              jurisdiction === 'cross_border' && 'bg-purple-100 text-purple-800'
            )}>
              {jurisdiction === 'india' ? 'Indian Law' : 
               jurisdiction === 'usa' ? 'US Law' : 
               jurisdiction === 'cross_border' ? 'Cross-Border' : 
               jurisdiction}
            </span>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="p-1.5 text-gray-400 hover:text-gray-600 transition-colors"
            title="Chat history"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
          
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1.5 text-gray-400 hover:text-gray-600 transition-colors"
            title={isExpanded ? 'Minimize' : 'Expand'}
          >
            {isExpanded ? (
              <Minimize2 className="h-4 w-4" />
            ) : (
              <Maximize2 className="h-4 w-4" />
            )}
          </button>

          <button
            className="p-1.5 text-gray-400 hover:text-gray-600 transition-colors"
            title="Settings"
          >
            <Settings className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 min-h-0">
        {/* Chat History Sidebar */}
        {showHistory && (
          <div className="w-80 border-r border-gray-200">
            <ChatHistory
              sessions={sessions}
              currentSessionId={currentSession?.id}
              onSessionSelect={handleSessionSelect}
              onSessionDelete={handleSessionDelete}
              onNewSession={handleNewSession}
            />
          </div>
        )}

        {/* Chat Messages Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Error Banner */}
          {error && (
            <div className="flex items-center justify-between p-3 bg-red-50 border-b border-red-200">
              <div className="flex items-center space-x-2">
                <AlertCircle className="h-4 w-4 text-red-600" />
                <span className="text-sm text-red-700">{error}</span>
              </div>
              <button
                onClick={handleRetryMessage}
                className="text-sm text-red-600 hover:text-red-700 font-medium"
              >
                Retry
              </button>
            </div>
          )}

          {/* Messages */}
          <div 
            ref={messagesContainerRef}
            className="flex-1 overflow-y-auto p-4 space-y-4"
          >
            {currentSession?.messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <MessageSquare className="h-12 w-12 text-gray-300 mb-4" />
                <h4 className="text-lg font-medium text-gray-900 mb-2">
                  Start a conversation
                </h4>
                <p className="text-gray-600 max-w-md">
                  Ask questions about your legal document. I can help with risk analysis, 
                  compliance checking, and jurisdiction-specific guidance.
                </p>
              </div>
            ) : (
              <>
                {currentSession?.messages.map((message) => (
                  <ChatMessage
                    key={message.id}
                    message={message}
                    onReferenceClick={onDocumentReferenceClick}
                  />
                ))}
                
                {/* Typing Indicator */}
                {typingIndicator && (
                  <TypingIndicator indicator={typingIndicator} />
                )}
                
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* Chat Input */}
          <ChatInput
            onSendMessage={handleSendMessage}
            onTyping={handleTyping}
            jurisdiction={jurisdiction || document?.metadata.jurisdiction}
            disabled={isLoading}
            placeholder={
              document 
                ? `Ask about ${document.name}...`
                : "Ask a legal question..."
            }
          />
        </div>
      </div>
    </div>
  );
}