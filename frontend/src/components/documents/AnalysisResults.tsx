'use client';

import React, { useState } from 'react';
import { 
  FileText, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  TrendingUp,
  BarChart3,
  Calendar,
  Users,
  MapPin,
  Scale,
  ChevronDown,
  ChevronRight,
  Info
} from 'lucide-react';
import { AnalysisResults as AnalysisResultsType, Risk, Obligation, ComplexityScore } from '../../types';

interface AnalysisResultsProps {
  results: AnalysisResultsType;
  className?: string;
}

interface ExecutiveSummaryProps {
  summary: AnalysisResultsType['summary'];
  jurisdictionAnalysis?: AnalysisResultsType['jurisdictionAnalysis'];
}

interface RiskVisualizationProps {
  risks: Risk[];
  jurisdictionAnalysis?: AnalysisResultsType['jurisdictionAnalysis'];
}

interface ObligationTimelineProps {
  obligations: Obligation[];
}

interface ComplexityDashboardProps {
  complexity: ComplexityScore;
  jurisdictionAnalysis?: AnalysisResultsType['jurisdictionAnalysis'];
}

const ExecutiveSummary: React.FC<ExecutiveSummaryProps> = ({ 
  summary, 
  jurisdictionAnalysis 
}) => {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
      <div 
        className="flex items-center justify-between p-4 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center space-x-3">
          <FileText className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Executive Summary</h3>
          {jurisdictionAnalysis && (
            <div className="flex items-center space-x-2">
              <MapPin className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600 capitalize">
                {jurisdictionAnalysis.primary} ({Math.round(jurisdictionAnalysis.confidence * 100)}% confidence)
              </span>
            </div>
          )}
        </div>
        {isExpanded ? (
          <ChevronDown className="w-5 h-5 text-gray-400" />
        ) : (
          <ChevronRight className="w-5 h-5 text-gray-400" />
        )}
      </div>
      
      {isExpanded && (
        <div className="px-4 pb-4 space-y-4">
          <div className="prose prose-sm max-w-none">
            <p className="text-gray-700 leading-relaxed">{summary.overview}</p>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Key Points</h4>
            <ul className="space-y-1">
              {summary.keyPoints.map((point, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-gray-700">{point}</span>
                </li>
              ))}
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Recommendations</h4>
            <ul className="space-y-1">
              {summary.recommendations.map((recommendation, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <Info className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-gray-700">{recommendation}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

const RiskVisualization: React.FC<RiskVisualizationProps> = ({ 
  risks, 
  jurisdictionAnalysis 
}) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [selectedRiskType, setSelectedRiskType] = useState<'all' | 'high' | 'medium' | 'low'>('all');

  const getRiskIcon = (type: Risk['type']) => {
    switch (type) {
      case 'high':
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'medium':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'low':
        return <AlertTriangle className="w-4 h-4 text-green-500" />;
      default:
        return <AlertTriangle className="w-4 h-4 text-gray-500" />;
    }
  };

  const getRiskColor = (type: Risk['type']) => {
    switch (type) {
      case 'high':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'medium':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'low':
        return 'bg-green-50 border-green-200 text-green-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const filteredRisks = selectedRiskType === 'all' 
    ? risks 
    : risks.filter(risk => risk.type === selectedRiskType);

  const riskCounts = {
    high: risks.filter(r => r.type === 'high').length,
    medium: risks.filter(r => r.type === 'medium').length,
    low: risks.filter(r => r.type === 'low').length
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
      <div 
        className="flex items-center justify-between p-4 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center space-x-3">
          <AlertTriangle className="w-5 h-5 text-red-600" />
          <h3 className="text-lg font-semibold text-gray-900">Risk Analysis</h3>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-red-500 rounded-full"></div>
              <span className="text-xs text-gray-600">{riskCounts.high} High</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <span className="text-xs text-gray-600">{riskCounts.medium} Medium</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-xs text-gray-600">{riskCounts.low} Low</span>
            </div>
          </div>
        </div>
        {isExpanded ? (
          <ChevronDown className="w-5 h-5 text-gray-400" />
        ) : (
          <ChevronRight className="w-5 h-5 text-gray-400" />
        )}
      </div>
      
      {isExpanded && (
        <div className="px-4 pb-4 space-y-4">
          {/* Risk Filter */}
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-700">Filter:</span>
            <div className="flex space-x-1">
              {(['all', 'high', 'medium', 'low'] as const).map((type) => (
                <button
                  key={type}
                  onClick={() => setSelectedRiskType(type)}
                  className={`px-3 py-1 text-xs rounded-full transition-colors duration-200 ${
                    selectedRiskType === type
                      ? 'bg-blue-100 text-blue-700 border border-blue-300'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {type === 'all' ? 'All' : `${type.charAt(0).toUpperCase()}${type.slice(1)}`}
                </button>
              ))}
            </div>
          </div>

          {/* Risk List */}
          <div className="space-y-3">
            {filteredRisks.map((risk) => (
              <div
                key={risk.id}
                className={`p-3 rounded-lg border ${getRiskColor(risk.type)}`}
              >
                <div className="flex items-start space-x-3">
                  {getRiskIcon(risk.type)}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-medium text-sm">{risk.category}</h4>
                      <span className="text-xs font-medium uppercase tracking-wide">
                        {risk.type}
                      </span>
                    </div>
                    <p className="text-sm mb-2">{risk.description}</p>
                    <div className="text-xs space-y-1">
                      <div>
                        <span className="font-medium">Impact:</span> {risk.impact}
                      </div>
                      {risk.mitigation && (
                        <div>
                          <span className="font-medium">Mitigation:</span> {risk.mitigation}
                        </div>
                      )}
                      {risk.section && (
                        <div>
                          <span className="font-medium">Section:</span> {risk.section}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredRisks.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <AlertTriangle className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>No {selectedRiskType === 'all' ? '' : selectedRiskType} risks found</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const ObligationTimeline: React.FC<ObligationTimelineProps> = ({ obligations }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState<'all' | 'pending' | 'completed' | 'overdue'>('all');

  const getStatusIcon = (status: Obligation['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'overdue':
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: Obligation['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'overdue':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'pending':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const filteredObligations = selectedStatus === 'all' 
    ? obligations 
    : obligations.filter(obligation => obligation.status === selectedStatus);

  const statusCounts = {
    pending: obligations.filter(o => o.status === 'pending').length,
    completed: obligations.filter(o => o.status === 'completed').length,
    overdue: obligations.filter(o => o.status === 'overdue').length
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
      <div 
        className="flex items-center justify-between p-4 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center space-x-3">
          <Calendar className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Obligations Timeline</h3>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <span className="text-xs text-gray-600">{statusCounts.pending} Pending</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-red-500 rounded-full"></div>
              <span className="text-xs text-gray-600">{statusCounts.overdue} Overdue</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-xs text-gray-600">{statusCounts.completed} Completed</span>
            </div>
          </div>
        </div>
        {isExpanded ? (
          <ChevronDown className="w-5 h-5 text-gray-400" />
        ) : (
          <ChevronRight className="w-5 h-5 text-gray-400" />
        )}
      </div>
      
      {isExpanded && (
        <div className="px-4 pb-4 space-y-4">
          {/* Status Filter */}
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-700">Filter:</span>
            <div className="flex space-x-1">
              {(['all', 'pending', 'overdue', 'completed'] as const).map((status) => (
                <button
                  key={status}
                  onClick={() => setSelectedStatus(status)}
                  className={`px-3 py-1 text-xs rounded-full transition-colors duration-200 ${
                    selectedStatus === status
                      ? 'bg-blue-100 text-blue-700 border border-blue-300'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {status === 'all' ? 'All' : `${status.charAt(0).toUpperCase()}${status.slice(1)}`}
                </button>
              ))}
            </div>
          </div>

          {/* Obligations List */}
          <div className="space-y-3">
            {filteredObligations.map((obligation) => (
              <div
                key={obligation.id}
                className={`p-3 rounded-lg border ${getStatusColor(obligation.status)}`}
              >
                <div className="flex items-start space-x-3">
                  {getStatusIcon(obligation.status)}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-medium text-sm">{obligation.party}</h4>
                      <span className="text-xs font-medium uppercase tracking-wide">
                        {obligation.status}
                      </span>
                    </div>
                    <p className="text-sm mb-2">{obligation.description}</p>
                    <div className="text-xs space-y-1">
                      {obligation.dueDate && (
                        <div>
                          <span className="font-medium">Due Date:</span> {new Date(obligation.dueDate).toLocaleDateString()}
                        </div>
                      )}
                      {obligation.section && (
                        <div>
                          <span className="font-medium">Section:</span> {obligation.section}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredObligations.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Calendar className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>No {selectedStatus === 'all' ? '' : selectedStatus} obligations found</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const ComplexityDashboard: React.FC<ComplexityDashboardProps> = ({ 
  complexity, 
  jurisdictionAnalysis 
}) => {
  const [isExpanded, setIsExpanded] = useState(true);

  const getComplexityColor = (score: number) => {
    if (score >= 80) return 'text-red-600 bg-red-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    if (score >= 40) return 'text-blue-600 bg-blue-100';
    return 'text-green-600 bg-green-100';
  };

  const getComplexityLabel = (score: number) => {
    if (score >= 80) return 'Very High';
    if (score >= 60) return 'High';
    if (score >= 40) return 'Medium';
    return 'Low';
  };

  const complexityMetrics = [
    { label: 'Overall', score: complexity.overall, icon: BarChart3 },
    { label: 'Legal', score: complexity.legal, icon: Scale },
    { label: 'Financial', score: complexity.financial, icon: TrendingUp },
    { label: 'Operational', score: complexity.operational, icon: Users }
  ];

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
      <div 
        className="flex items-center justify-between p-4 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center space-x-3">
          <BarChart3 className="w-5 h-5 text-purple-600" />
          <h3 className="text-lg font-semibold text-gray-900">Complexity Analysis</h3>
          <div className={`px-2 py-1 rounded-full text-xs font-medium ${getComplexityColor(complexity.overall)}`}>
            {getComplexityLabel(complexity.overall)} ({complexity.overall}/100)
          </div>
        </div>
        {isExpanded ? (
          <ChevronDown className="w-5 h-5 text-gray-400" />
        ) : (
          <ChevronRight className="w-5 h-5 text-gray-400" />
        )}
      </div>
      
      {isExpanded && (
        <div className="px-4 pb-4 space-y-4">
          {/* Complexity Metrics */}
          <div className="grid grid-cols-2 gap-4">
            {complexityMetrics.map((metric) => {
              const Icon = metric.icon;
              return (
                <div key={metric.label} className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Icon className="w-4 h-4 text-gray-600" />
                      <span className="text-sm font-medium text-gray-700">{metric.label}</span>
                    </div>
                    <span className={`text-xs font-medium px-2 py-1 rounded ${getComplexityColor(metric.score)}`}>
                      {metric.score}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-300 ${
                        metric.score >= 80 ? 'bg-red-500' :
                        metric.score >= 60 ? 'bg-yellow-500' :
                        metric.score >= 40 ? 'bg-blue-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${metric.score}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Explanation */}
          <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
            <h4 className="font-medium text-blue-900 mb-2">Analysis Explanation</h4>
            <p className="text-sm text-blue-800">{complexity.explanation}</p>
          </div>

          {/* Jurisdiction-specific complexity factors */}
          {jurisdictionAnalysis && (
            <div className="p-3 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">Jurisdiction-Specific Factors</h4>
              <div className="text-sm text-gray-700">
                <p>Primary jurisdiction: <span className="font-medium capitalize">{jurisdictionAnalysis.primary}</span></p>
                <p>Confidence: <span className="font-medium">{Math.round(jurisdictionAnalysis.confidence * 100)}%</span></p>
                {jurisdictionAnalysis.primary === 'cross_border' && (
                  <p className="text-yellow-700 mt-1">
                    Cross-border complexity may require additional legal review in multiple jurisdictions.
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({ 
  results, 
  className = '' 
}) => {
  return (
    <div className={`space-y-6 ${className}`}>
      <ExecutiveSummary 
        summary={results.summary} 
        jurisdictionAnalysis={results.jurisdictionAnalysis}
      />
      
      <RiskVisualization 
        risks={results.risks} 
        jurisdictionAnalysis={results.jurisdictionAnalysis}
      />
      
      <ObligationTimeline obligations={results.obligations} />
      
      <ComplexityDashboard 
        complexity={results.complexity} 
        jurisdictionAnalysis={results.jurisdictionAnalysis}
      />
    </div>
  );
};

export default AnalysisResults;