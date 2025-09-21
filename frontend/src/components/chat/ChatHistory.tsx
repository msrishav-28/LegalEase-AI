import React, { useState, useCallback } from 'react';
import { clsx } from 'clsx';
import { 
  History, 
  Search, 
  Filter, 
  Calendar,
  FileText,
  Trash2,
  MoreVertical
} from 'lucide-react';
import { ChatSession, Jurisdiction } from '@/types';
import JurisdictionBadge from './JurisdictionBadge';

interface ChatHistoryProps {
  sessions: ChatSession[];
  currentSessionId?: string;
  onSessionSelect: (session: ChatSession) => void;
  onSessionDelete?: (sessionId: string) => void;
  onNewSession?: () => void;
  className?: string;
}

const getJurisdictionBadge = (jurisdiction?: Jurisdiction) => {
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

export default function ChatHistory({
  sessions,
  currentSessionId,
  onSessionSelect,
  onSessionDelete,
  onNewSession,
  className
}: ChatHistoryProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterJurisdiction, setFilterJurisdiction] = useState<Jurisdiction | 'all'>('all');
  const [showFilters, setShowFilters] = useState(false);

  // Filter sessions based on search and jurisdiction
  const filteredSessions = sessions.filter(session => {
    const matchesSearch = !searchQuery || 
      session.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      session.messages.some(msg => 
        msg.content.toLowerCase().includes(searchQuery.toLowerCase())
      );
    
    const matchesJurisdiction = filterJurisdiction === 'all' || 
      session.jurisdiction === filterJurisdiction;
    
    return matchesSearch && matchesJurisdiction;
  });

  // Group sessions by date
  const groupedSessions = filteredSessions.reduce((groups, session) => {
    const date = new Date(session.updatedAt).toDateString();
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(session);
    return groups;
  }, {} as Record<string, ChatSession[]>);

  const handleSessionClick = useCallback((session: ChatSession) => {
    onSessionSelect(session);
  }, [onSessionSelect]);

  const handleDeleteSession = useCallback((e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    if (onSessionDelete) {
      onSessionDelete(sessionId);
    }
  }, [onSessionDelete]);

  const getSessionPreview = (session: ChatSession): string => {
    const lastUserMessage = session.messages
      .filter(msg => msg.role === 'user')
      .pop();
    
    return lastUserMessage?.content.slice(0, 100) + '...' || 'No messages';
  };

  const formatRelativeTime = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 1) {
      return 'Just now';
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`;
    } else if (diffInHours < 48) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString();
    }
  };

  return (
    <div className={clsx('flex flex-col h-full bg-white border-r border-gray-200', className)}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <History className="h-5 w-5 text-gray-600" />
            <h2 className="text-lg font-semibold text-gray-900">Chat History</h2>
          </div>
          
          {onNewSession && (
            <button
              onClick={onNewSession}
              className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              New Chat
            </button>
          )}
        </div>

        {/* Search */}
        <div className="relative mb-3">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
          />
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={clsx(
              'flex items-center space-x-1 px-2 py-1 text-xs rounded-md transition-colors',
              showFilters 
                ? 'bg-blue-100 text-blue-700' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            )}
          >
            <Filter className="h-3 w-3" />
            <span>Filters</span>
          </button>
          
          {showFilters && (
            <select
              value={filterJurisdiction}
              onChange={(e) => setFilterJurisdiction(e.target.value as Jurisdiction | 'all')}
              className="text-xs border border-gray-300 rounded-md px-2 py-1 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
            >
              <option value="all">All Jurisdictions</option>
              <option value="india">India</option>
              <option value="usa">USA</option>
              <option value="cross_border">Cross-Border</option>
            </select>
          )}
        </div>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto">
        {Object.keys(groupedSessions).length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <History className="h-12 w-12 mx-auto mb-3 text-gray-300" />
            <p className="text-sm">No chat sessions found</p>
            {searchQuery && (
              <p className="text-xs mt-1">Try adjusting your search terms</p>
            )}
          </div>
        ) : (
          Object.entries(groupedSessions)
            .sort(([a], [b]) => new Date(b).getTime() - new Date(a).getTime())
            .map(([date, dateSessions]) => (
              <div key={date} className="mb-4">
                {/* Date Header */}
                <div className="sticky top-0 bg-gray-50 px-4 py-2 border-b border-gray-100">
                  <div className="flex items-center space-x-2">
                    <Calendar className="h-3 w-3 text-gray-400" />
                    <span className="text-xs font-medium text-gray-600">
                      {date === new Date().toDateString() ? 'Today' : 
                       date === new Date(Date.now() - 86400000).toDateString() ? 'Yesterday' : 
                       date}
                    </span>
                  </div>
                </div>

                {/* Sessions for this date */}
                <div className="space-y-1 p-2">
                  {dateSessions
                    .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
                    .map((session) => {
                      const jurisdictionBadge = getJurisdictionBadge(session.jurisdiction);
                      const isActive = session.id === currentSessionId;
                      
                      return (
                        <div
                          key={session.id}
                          onClick={() => handleSessionClick(session)}
                          className={clsx(
                            'group relative p-3 rounded-lg cursor-pointer transition-colors',
                            isActive 
                              ? 'bg-blue-50 border border-blue-200' 
                              : 'hover:bg-gray-50 border border-transparent'
                          )}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1 min-w-0">
                              {/* Session title and jurisdiction */}
                              <div className="flex items-center space-x-2 mb-1">
                                <FileText className="h-3 w-3 text-gray-400 flex-shrink-0" />
                                <span className="text-sm font-medium text-gray-900 truncate">
                                  {session.title || `Chat ${session.id.slice(0, 8)}`}
                                </span>
                                {jurisdictionBadge && (
                                  <JurisdictionBadge 
                                    badge={jurisdictionBadge} 
                                    size="sm" 
                                    showConfidence={false} 
                                  />
                                )}
                              </div>
                              
                              {/* Preview and metadata */}
                              <p className="text-xs text-gray-600 line-clamp-2 mb-1">
                                {getSessionPreview(session)}
                              </p>
                              
                              <div className="flex items-center justify-between">
                                <span className="text-xs text-gray-500">
                                  {session.messages.length} messages
                                </span>
                                <span className="text-xs text-gray-500">
                                  {formatRelativeTime(session.updatedAt)}
                                </span>
                              </div>
                            </div>

                            {/* Actions */}
                            {onSessionDelete && (
                              <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button
                                  onClick={(e) => handleDeleteSession(e, session.id)}
                                  className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                                  title="Delete session"
                                >
                                  <Trash2 className="h-3 w-3" />
                                </button>
                                <button
                                  onClick={(e) => e.stopPropagation()}
                                  className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                                  title="More options"
                                >
                                  <MoreVertical className="h-3 w-3" />
                                </button>
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                </div>
              </div>
            ))
        )}
      </div>
    </div>
  );
}