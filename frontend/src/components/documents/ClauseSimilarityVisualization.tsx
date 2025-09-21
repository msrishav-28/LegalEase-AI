'use client';

import React, { useMemo } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Target, 
  Layers,
  ArrowRight,
  CheckCircle,
  AlertCircle,
  Info
} from 'lucide-react';
import { ClauseSimilarity, DocumentComparison } from '@/types';

interface ClauseSimilarityVisualizationProps {
  similarities: ClauseSimilarity[];
  comparison: DocumentComparison;
  onSimilaritySelect?: (similarity: ClauseSimilarity) => void;
  selectedSimilarity?: ClauseSimilarity | null;
  className?: string;
}

interface SimilarityGroup {
  type: 'identical' | 'similar' | 'related';
  similarities: ClauseSimilarity[];
  averageScore: number;
  count: number;
}

export const ClauseSimilarityVisualization: React.FC<ClauseSimilarityVisualizationProps> = ({
  similarities,
  comparison,
  onSimilaritySelect,
  selectedSimilarity,
  className = ''
}) => {
  // Group similarities by type
  const similarityGroups = useMemo(() => {
    const groups: Record<string, SimilarityGroup> = {
      identical: { type: 'identical', similarities: [], averageScore: 0, count: 0 },
      similar: { type: 'similar', similarities: [], averageScore: 0, count: 0 },
      related: { type: 'related', similarities: [], averageScore: 0, count: 0 }
    };

    similarities.forEach(sim => {
      groups[sim.type].similarities.push(sim);
      groups[sim.type].count++;
    });

    // Calculate average scores
    Object.values(groups).forEach(group => {
      if (group.count > 0) {
        group.averageScore = group.similarities.reduce((sum, sim) => sum + sim.similarityScore, 0) / group.count;
      }
    });

    return groups;
  }, [similarities]);

  // Calculate distribution metrics
  const distributionMetrics = useMemo(() => {
    const totalSimilarities = similarities.length;
    const scoreRanges = {
      high: similarities.filter(s => s.similarityScore >= 0.8).length,
      medium: similarities.filter(s => s.similarityScore >= 0.6 && s.similarityScore < 0.8).length,
      low: similarities.filter(s => s.similarityScore < 0.6).length
    };

    const sectionCoverage = new Set();
    similarities.forEach(sim => {
      sectionCoverage.add(sim.document1Clause.section);
      sectionCoverage.add(sim.document2Clause.section);
    });

    return {
      total: totalSimilarities,
      scoreRanges,
      sectionCoverage: sectionCoverage.size,
      averageScore: totalSimilarities > 0 
        ? similarities.reduce((sum, sim) => sum + sim.similarityScore, 0) / totalSimilarities 
        : 0
    };
  }, [similarities]);

  // Get similarity type color and icon
  const getSimilarityTypeInfo = (type: string) => {
    switch (type) {
      case 'identical':
        return {
          color: 'text-green-600 bg-green-50 border-green-200',
          icon: CheckCircle,
          label: 'Identical',
          description: 'Exact or near-exact matches'
        };
      case 'similar':
        return {
          color: 'text-blue-600 bg-blue-50 border-blue-200',
          icon: Target,
          label: 'Similar',
          description: 'High similarity with minor differences'
        };
      case 'related':
        return {
          color: 'text-yellow-600 bg-yellow-50 border-yellow-200',
          icon: Info,
          label: 'Related',
          description: 'Conceptually related clauses'
        };
      default:
        return {
          color: 'text-gray-600 bg-gray-50 border-gray-200',
          icon: Info,
          label: 'Unknown',
          description: 'Unknown similarity type'
        };
    }
  };

  // Get score color
  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Overview Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Similarities</p>
              <p className="text-2xl font-semibold text-gray-900">
                {distributionMetrics.total}
              </p>
            </div>
            <Layers className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Average Score</p>
              <p className={`text-2xl font-semibold ${getScoreColor(distributionMetrics.averageScore)}`}>
                {Math.round(distributionMetrics.averageScore * 100)}%
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">High Similarity</p>
              <p className="text-2xl font-semibold text-green-600">
                {distributionMetrics.scoreRanges.high}
              </p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Sections Covered</p>
              <p className="text-2xl font-semibold text-blue-600">
                {distributionMetrics.sectionCoverage}
              </p>
            </div>
            <BarChart3 className="w-8 h-8 text-blue-500" />
          </div>
        </div>
      </div>

      {/* Similarity Type Distribution */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Similarity Distribution
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.values(similarityGroups).map((group) => {
            const typeInfo = getSimilarityTypeInfo(group.type);
            const Icon = typeInfo.icon;
            
            return (
              <div
                key={group.type}
                className={`p-4 rounded-lg border ${typeInfo.color}`}
              >
                <div className="flex items-center space-x-3 mb-3">
                  <Icon className="w-5 h-5" />
                  <div>
                    <h4 className="font-medium">{typeInfo.label}</h4>
                    <p className="text-xs opacity-75">{typeInfo.description}</p>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Count:</span>
                    <span className="font-medium">{group.count}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Avg Score:</span>
                    <span className="font-medium">
                      {Math.round(group.averageScore * 100)}%
                    </span>
                  </div>
                  
                  {/* Progress bar */}
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="h-2 rounded-full bg-current opacity-60"
                      style={{ width: `${(group.count / distributionMetrics.total) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Score Distribution Chart */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Score Distribution
        </h3>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">High (80-100%)</span>
            <div className="flex items-center space-x-2">
              <div className="w-32 bg-gray-200 rounded-full h-2">
                <div
                  className="h-2 rounded-full bg-green-500"
                  style={{ 
                    width: `${distributionMetrics.total > 0 
                      ? (distributionMetrics.scoreRanges.high / distributionMetrics.total) * 100 
                      : 0}%` 
                  }}
                />
              </div>
              <span className="text-sm font-medium text-gray-900 w-8">
                {distributionMetrics.scoreRanges.high}
              </span>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Medium (60-79%)</span>
            <div className="flex items-center space-x-2">
              <div className="w-32 bg-gray-200 rounded-full h-2">
                <div
                  className="h-2 rounded-full bg-yellow-500"
                  style={{ 
                    width: `${distributionMetrics.total > 0 
                      ? (distributionMetrics.scoreRanges.medium / distributionMetrics.total) * 100 
                      : 0}%` 
                  }}
                />
              </div>
              <span className="text-sm font-medium text-gray-900 w-8">
                {distributionMetrics.scoreRanges.medium}
              </span>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Low (0-59%)</span>
            <div className="flex items-center space-x-2">
              <div className="w-32 bg-gray-200 rounded-full h-2">
                <div
                  className="h-2 rounded-full bg-red-500"
                  style={{ 
                    width: `${distributionMetrics.total > 0 
                      ? (distributionMetrics.scoreRanges.low / distributionMetrics.total) * 100 
                      : 0}%` 
                  }}
                />
              </div>
              <span className="text-sm font-medium text-gray-900 w-8">
                {distributionMetrics.scoreRanges.low}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Top Similarities List */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            Top Similarities
          </h3>
        </div>
        
        <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
          {similarities
            .sort((a, b) => b.similarityScore - a.similarityScore)
            .slice(0, 10)
            .map((similarity) => {
              const typeInfo = getSimilarityTypeInfo(similarity.type);
              const Icon = typeInfo.icon;
              const isSelected = selectedSimilarity?.id === similarity.id;
              
              return (
                <div
                  key={similarity.id}
                  onClick={() => onSimilaritySelect?.(similarity)}
                  className={`p-4 cursor-pointer transition-colors ${
                    isSelected ? 'bg-blue-50 border-l-4 border-l-blue-500' : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-start space-x-4">
                    <Icon className={`w-5 h-5 mt-1 ${typeInfo.color.split(' ')[0]}`} />
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-2">
                        <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${typeInfo.color}`}>
                          {typeInfo.label}
                        </span>
                        <span className={`text-sm font-medium ${getScoreColor(similarity.similarityScore)}`}>
                          {Math.round(similarity.similarityScore * 100)}%
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <p className="text-xs text-gray-500 mb-1">
                            {comparison.document1.name} - {similarity.document1Clause.section}
                          </p>
                          <p className="text-sm text-gray-900 line-clamp-2">
                            {similarity.document1Clause.content}
                          </p>
                        </div>
                        
                        <div>
                          <p className="text-xs text-gray-500 mb-1">
                            {comparison.document2.name} - {similarity.document2Clause.section}
                          </p>
                          <p className="text-sm text-gray-900 line-clamp-2">
                            {similarity.document2Clause.content}
                          </p>
                        </div>
                      </div>
                      
                      {similarity.differences && similarity.differences.length > 0 && (
                        <div className="mt-2">
                          <p className="text-xs text-gray-500 mb-1">Key Differences:</p>
                          <ul className="text-xs text-gray-600 space-y-1">
                            {similarity.differences.slice(0, 2).map((diff, index) => (
                              <li key={index} className="flex items-center space-x-1">
                                <AlertCircle className="w-3 h-3 text-yellow-500" />
                                <span>{diff}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                    
                    <ArrowRight className="w-4 h-4 text-gray-400 mt-2" />
                  </div>
                </div>
              );
            })}
        </div>
        
        {similarities.length === 0 && (
          <div className="p-8 text-center">
            <Info className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h4 className="text-lg font-medium text-gray-900 mb-2">
              No Similarities Found
            </h4>
            <p className="text-gray-600">
              No similar clauses were detected between the documents.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ClauseSimilarityVisualization;