'use client';

import React, { useState, useEffect } from 'react';
import { JurisdictionDetection, Jurisdiction } from '@/types';

interface JurisdictionAnalysisProps {
  documentId?: string;
  initialDetection?: JurisdictionDetection;
  onJurisdictionChange?: (jurisdiction: Jurisdiction) => void;
  className?: string;
}

const INDIAN_STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
  'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
  'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
  'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
  'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Chandigarh', 'Dadra and Nagar Haveli',
  'Daman and Diu', 'Lakshadweep', 'Puducherry'
];

const US_STATES = [
  'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado',
  'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho',
  'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana',
  'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
  'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada',
  'New Hampshire', 'New Jersey', 'New Mexico', 'New York',
  'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon',
  'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota',
  'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
  'West Virginia', 'Wisconsin', 'Wyoming', 'District of Columbia'
];

export const JurisdictionAnalysis: React.FC<JurisdictionAnalysisProps> = ({
  documentId,
  initialDetection,
  onJurisdictionChange,
  className = ''
}) => {
  const [detection, setDetection] = useState<JurisdictionDetection | null>(initialDetection || null);
  const [selectedJurisdiction, setSelectedJurisdiction] = useState<Jurisdiction>('unknown');
  const [selectedState, setSelectedState] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'india' | 'usa' | 'compare'>('india');

  useEffect(() => {
    if (initialDetection) {
      setDetection(initialDetection);
      setSelectedJurisdiction(initialDetection.jurisdiction);
      if (initialDetection.usState) {
        setSelectedState(initialDetection.usState);
      }
    }
  }, [initialDetection]);

  const handleJurisdictionDetection = async () => {
    if (!documentId) return;
    
    setIsLoading(true);
    try {
      // This would call the backend API for jurisdiction detection
      // const response = await api.post(`/api/jurisdiction/detect`, { documentId });
      // setDetection(response.data);
      
      // Mock detection for now
      const mockDetection: JurisdictionDetection = {
        jurisdiction: 'india',
        confidence: 0.85,
        scores: {
          india: 0.85,
          usa: 0.15
        },
        detectedElements: ['Indian Contract Act', 'Rupees', 'Delhi High Court']
      };
      setDetection(mockDetection);
      setSelectedJurisdiction(mockDetection.jurisdiction);
    } catch (error) {
      console.error('Failed to detect jurisdiction:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleJurisdictionSelect = (jurisdiction: Jurisdiction) => {
    setSelectedJurisdiction(jurisdiction);
    onJurisdictionChange?.(jurisdiction);
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-100';
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getConfidenceText = (confidence: number) => {
    if (confidence >= 0.8) return 'High Confidence';
    if (confidence >= 0.6) return 'Medium Confidence';
    return 'Low Confidence';
  };

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Jurisdiction Analysis</h3>
        {documentId && (
          <button
            onClick={handleJurisdictionDetection}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Detecting...' : 'Auto-Detect'}
          </button>
        )}
      </div>

      {/* Detection Results */}
      {detection && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-medium text-gray-900">Detection Results</h4>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getConfidenceColor(detection.confidence)}`}>
              {getConfidenceText(detection.confidence)} ({Math.round(detection.confidence * 100)}%)
            </span>
          </div>
          
          <div className="grid grid-cols-2 gap-4 mb-3">
            <div className="flex items-center justify-between p-3 bg-white rounded border">
              <span className="font-medium">India</span>
              <div className="flex items-center">
                <div className="w-20 bg-gray-200 rounded-full h-2 mr-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full" 
                    style={{ width: `${detection.scores.india * 100}%` }}
                  ></div>
                </div>
                <span className="text-sm text-gray-600">{Math.round(detection.scores.india * 100)}%</span>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-white rounded border">
              <span className="font-medium">USA</span>
              <div className="flex items-center">
                <div className="w-20 bg-gray-200 rounded-full h-2 mr-2">
                  <div 
                    className="bg-red-600 h-2 rounded-full" 
                    style={{ width: `${detection.scores.usa * 100}%` }}
                  ></div>
                </div>
                <span className="text-sm text-gray-600">{Math.round(detection.scores.usa * 100)}%</span>
              </div>
            </div>
          </div>

          {detection.detectedElements.length > 0 && (
            <div>
              <h5 className="text-sm font-medium text-gray-700 mb-2">Detected Elements:</h5>
              <div className="flex flex-wrap gap-2">
                {detection.detectedElements.map((element, index) => (
                  <span 
                    key={index}
                    className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                  >
                    {element}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Manual Jurisdiction Selection */}
      <div className="mb-6">
        <h4 className="font-medium text-gray-900 mb-3">Select Jurisdiction</h4>
        <div className="grid grid-cols-3 gap-2">
          <button
            onClick={() => handleJurisdictionSelect('india')}
            className={`p-3 rounded-lg border-2 text-center transition-colors ${
              selectedJurisdiction === 'india'
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="font-medium">India</div>
            <div className="text-sm text-gray-500">Indian Law</div>
          </button>
          
          <button
            onClick={() => handleJurisdictionSelect('usa')}
            className={`p-3 rounded-lg border-2 text-center transition-colors ${
              selectedJurisdiction === 'usa'
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="font-medium">USA</div>
            <div className="text-sm text-gray-500">US Law</div>
          </button>
          
          <button
            onClick={() => handleJurisdictionSelect('cross_border')}
            className={`p-3 rounded-lg border-2 text-center transition-colors ${
              selectedJurisdiction === 'cross_border'
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="font-medium">Cross-Border</div>
            <div className="text-sm text-gray-500">Multi-Jurisdiction</div>
          </button>
        </div>
      </div>

      {/* State Selection */}
      {(selectedJurisdiction === 'india' || selectedJurisdiction === 'usa') && (
        <div className="mb-6">
          <h4 className="font-medium text-gray-900 mb-3">
            Select {selectedJurisdiction === 'india' ? 'State/UT' : 'State'}
          </h4>
          <select
            value={selectedState}
            onChange={(e) => setSelectedState(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Select {selectedJurisdiction === 'india' ? 'State/UT' : 'State'}</option>
            {(selectedJurisdiction === 'india' ? INDIAN_STATES : US_STATES).map((state) => (
              <option key={state} value={state}>{state}</option>
            ))}
          </select>
        </div>
      )}

      {/* Jurisdiction Comparison Tabs */}
      <div className="border-t pt-6">
        <div className="flex space-x-1 mb-4">
          <button
            onClick={() => setActiveTab('india')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'india'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            India Analysis
          </button>
          <button
            onClick={() => setActiveTab('usa')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'usa'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            USA Analysis
          </button>
          <button
            onClick={() => setActiveTab('compare')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'compare'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Compare
          </button>
        </div>

        <div className="min-h-[200px] p-4 bg-gray-50 rounded-lg">
          {activeTab === 'india' && (
            <div className="text-center text-gray-500">
              Indian legal analysis will be displayed here
            </div>
          )}
          {activeTab === 'usa' && (
            <div className="text-center text-gray-500">
              US legal analysis will be displayed here
            </div>
          )}
          {activeTab === 'compare' && (
            <div className="text-center text-gray-500">
              Cross-border comparison will be displayed here
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default JurisdictionAnalysis;