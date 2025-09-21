'use client';

import React, { useState, useEffect } from 'react';
import { CrossBorderAnalysis, EnforceabilityComparison, TaxImplications, FormalitiesComparison, ComplianceGap } from '@/types';

interface JurisdictionComparisonProps {
  documentId?: string;
  analysis?: CrossBorderAnalysis;
  onAnalysisUpdate?: (analysis: CrossBorderAnalysis) => void;
  className?: string;
}

export const JurisdictionComparison: React.FC<JurisdictionComparisonProps> = ({
  documentId,
  analysis,
  onAnalysisUpdate,
  className = ''
}) => {
  const [activeSection, setActiveSection] = useState<'enforceability' | 'formalities' | 'tax' | 'recommendations'>('enforceability');
  const [isLoading, setIsLoading] = useState(false);
  const [analysisData, setAnalysisData] = useState<CrossBorderAnalysis | null>(analysis || null);

  useEffect(() => {
    if (analysis) {
      setAnalysisData(analysis);
    }
  }, [analysis]);

  const performComparison = async () => {
    if (!documentId) return;
    
    setIsLoading(true);
    try {
      // This would call the backend API for cross-border comparison
      // const response = await api.post(`/api/jurisdiction/compare`, { documentId });
      
      // Enhanced mock analysis data with comprehensive cross-border comparison
      const mockAnalysis: CrossBorderAnalysis = {
        enforceabilityComparison: {
          india: {
            formalities: [
              'Stamp duty payment required',
              'Registration with Sub-Registrar (for certain agreements)',
              'Two witnesses required for execution',
              'Notarization recommended but not mandatory'
            ],
            requirements: [
              'Compliance with Indian Contract Act, 1872',
              'Consideration must be lawful and adequate',
              'Parties must have contractual capacity',
              'Free consent without coercion, fraud, or misrepresentation'
            ],
            challenges: [
              'Complex stamp duty variations across states',
              'Lengthy court procedures for enforcement',
              'Limited recognition of foreign arbitral awards',
              'Currency restrictions under FEMA'
            ]
          },
          usa: {
            formalities: [
              'Notarization required in most states',
              'Witness requirements vary by state',
              'Recording may be required for real estate',
              'Acknowledgment of signatures'
            ],
            requirements: [
              'Offer, acceptance, and consideration',
              'Legal capacity of parties',
              'Lawful subject matter',
              'Compliance with Statute of Frauds where applicable'
            ],
            challenges: [
              'State law variations create complexity',
              'Federal vs state jurisdiction issues',
              'Discovery process can be extensive and costly',
              'Class action lawsuit risks'
            ]
          },
          recommendations: [
            'Include choice of law clause favoring business-friendly jurisdiction',
            'Specify dispute resolution mechanism (arbitration preferred)',
            'Ensure compliance with both jurisdictions\' formality requirements',
            'Consider governing law based on primary business operations',
            'Include force majeure clauses addressing both jurisdictions'
          ]
        },
        formalitiesComparison: {
          india: {
            stampDuty: {
              required: true,
              amount: 'Varies by state (₹100 to ₹50,000+)',
              exemptions: ['Government transactions', 'Charitable organizations', 'Cooperative societies']
            },
            registration: {
              required: false,
              authority: 'Sub-Registrar Office',
              timeline: 'Optional for most commercial agreements'
            },
            witnesses: {
              required: true,
              count: 2,
              requirements: ['Adult witnesses', 'Valid identification', 'Present during execution']
            },
            notarization: {
              required: false,
              type: 'Recommended for international agreements'
            }
          },
          usa: {
            notarization: {
              required: true,
              type: 'Acknowledgment or Jurat',
              stateRequirements: ['Notary public commission', 'Valid identification', 'Personal appearance']
            },
            witnesses: {
              required: false,
              count: 0,
              requirements: ['Varies by state and document type']
            },
            recording: {
              required: false,
              authority: 'County Recorder\'s Office',
              fees: '$10-$50 per document'
            },
            acknowledgment: {
              required: true,
              type: 'Notarial acknowledgment of signature'
            }
          },
          differences: [
            'India requires stamp duty; USA does not',
            'USA requires notarization; India recommends but doesn\'t mandate',
            'India requires witnesses; USA generally does not',
            'USA has standardized notarial procedures; India has varied state requirements'
          ],
          recommendations: [
            'Satisfy both jurisdictions\' requirements for maximum enforceability',
            'Use notarization and witnesses for international agreements',
            'Pay appropriate stamp duty for Indian enforceability',
            'Consider apostille for international document recognition'
          ]
        },
        taxImplications: {
          indiaImplications: [
            'GST applicable on services at 18%',
            'TDS requirements under Income Tax Act',
            'FEMA compliance for foreign exchange transactions',
            'Transfer pricing regulations for related party transactions',
            'Withholding tax on payments to non-residents'
          ],
          usImplications: [
            'Federal income tax on business income',
            'State tax variations (0% to 13.3%)',
            'Sales tax on goods and certain services',
            'Withholding requirements for foreign entities',
            'FATCA reporting for foreign accounts'
          ],
          dtaaConsiderations: [
            'India-US DTAA provides relief from double taxation',
            'Reduced withholding tax rates on dividends, interest, and royalties',
            'Mutual agreement procedure for dispute resolution',
            'Tie-breaker rules for tax residency determination',
            'Exchange of information provisions'
          ],
          comparisonSummary: 'India has higher service tax rates (18% GST vs varying US sales tax), but DTAA provides significant relief for cross-border transactions. US has more complex state-level variations.',
          recommendedStructure: 'Consider establishing entities in both jurisdictions to optimize tax efficiency and ensure compliance with local requirements.'
        },
        recommendedGoverningLaw: 'Delaware Law (for commercial flexibility) or Singapore Law (for international neutrality)',
        disputeResolutionRecommendation: 'Singapore International Arbitration Centre (SIAC) for neutral venue with expertise in India-US disputes',
        complianceGaps: [
          {
            jurisdiction: 'india',
            requirement: 'FEMA compliance for foreign exchange',
            status: 'missing',
            impact: 'high',
            recommendation: 'Obtain necessary approvals from RBI for foreign exchange transactions'
          },
          {
            jurisdiction: 'usa',
            requirement: 'State-specific notarization requirements',
            status: 'partial',
            impact: 'medium',
            recommendation: 'Ensure notarization meets requirements of the governing state'
          },
          {
            jurisdiction: 'india',
            requirement: 'GST registration for service providers',
            status: 'missing',
            impact: 'medium',
            recommendation: 'Register for GST if annual turnover exceeds ₹20 lakhs'
          }
        ]
      };
      
      setAnalysisData(mockAnalysis);
      onAnalysisUpdate?.(mockAnalysis);
    } catch (error) {
      console.error('Failed to perform cross-border comparison:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderEnforceabilityComparison = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h4 className="font-medium text-gray-900">Enforceability Comparison</h4>
        <button
          onClick={performComparison}
          disabled={isLoading}
          className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {isLoading && (
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          )}
          <span>{isLoading ? 'Analyzing...' : 'Perform Comparison'}</span>
        </button>
      </div>

      {analysisData?.enforceabilityComparison ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* India Enforceability */}
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <div className="bg-orange-50 px-4 py-3 border-b border-orange-200">
              <div className="flex items-center">
                <div className="w-6 h-4 bg-orange-500 rounded-sm mr-3"></div>
                <h5 className="font-semibold text-gray-900">India</h5>
              </div>
            </div>
            
            <div className="p-4 space-y-4">
              <div>
                <h6 className="text-sm font-medium text-gray-700 mb-2">Formalities Required</h6>
                <ul className="space-y-2">
                  {analysisData.enforceabilityComparison.india.formalities.map((formality, index) => (
                    <li key={index} className="flex items-start text-sm text-gray-600">
                      <svg className="w-4 h-4 text-green-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      {formality}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h6 className="text-sm font-medium text-gray-700 mb-2">Legal Requirements</h6>
                <ul className="space-y-2">
                  {analysisData.enforceabilityComparison.india.requirements.map((requirement, index) => (
                    <li key={index} className="flex items-start text-sm text-gray-600">
                      <svg className="w-4 h-4 text-blue-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      {requirement}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h6 className="text-sm font-medium text-gray-700 mb-2">Enforcement Challenges</h6>
                <ul className="space-y-2">
                  {analysisData.enforceabilityComparison.india.challenges.map((challenge, index) => (
                    <li key={index} className="flex items-start text-sm text-gray-600">
                      <svg className="w-4 h-4 text-red-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                      </svg>
                      {challenge}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* USA Enforceability */}
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <div className="bg-blue-50 px-4 py-3 border-b border-blue-200">
              <div className="flex items-center">
                <div className="w-6 h-4 bg-blue-500 rounded-sm mr-3"></div>
                <h5 className="font-semibold text-gray-900">USA</h5>
              </div>
            </div>
            
            <div className="p-4 space-y-4">
              <div>
                <h6 className="text-sm font-medium text-gray-700 mb-2">Formalities Required</h6>
                <ul className="space-y-2">
                  {analysisData.enforceabilityComparison.usa.formalities.map((formality, index) => (
                    <li key={index} className="flex items-start text-sm text-gray-600">
                      <svg className="w-4 h-4 text-green-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      {formality}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h6 className="text-sm font-medium text-gray-700 mb-2">Legal Requirements</h6>
                <ul className="space-y-2">
                  {analysisData.enforceabilityComparison.usa.requirements.map((requirement, index) => (
                    <li key={index} className="flex items-start text-sm text-gray-600">
                      <svg className="w-4 h-4 text-blue-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      {requirement}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h6 className="text-sm font-medium text-gray-700 mb-2">Enforcement Challenges</h6>
                <ul className="space-y-2">
                  {analysisData.enforceabilityComparison.usa.challenges.map((challenge, index) => (
                    <li key={index} className="flex items-start text-sm text-gray-600">
                      <svg className="w-4 h-4 text-red-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                      </svg>
                      {challenge}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <div className="max-w-sm mx-auto">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No Comparison Available</h3>
            <p className="mt-1 text-sm text-gray-500">Click "Perform Comparison" to analyze enforceability differences between jurisdictions.</p>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {analysisData?.enforceabilityComparison?.recommendations && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h5 className="font-medium text-blue-800 mb-3">Enforceability Recommendations</h5>
          <ul className="space-y-2">
            {analysisData.enforceabilityComparison.recommendations.map((recommendation, index) => (
              <li key={index} className="flex items-start text-sm text-blue-700">
                <svg className="w-4 h-4 text-blue-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                </svg>
                {recommendation}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );

  const renderFormalitiesComparison = () => (
    <div className="space-y-6">
      <h4 className="font-medium text-gray-900">Formalities Difference Highlighting</h4>
      
      {analysisData?.formalitiesComparison ? (
        <div className="space-y-6">
          {/* Side-by-side comparison */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* India Formalities */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div className="bg-orange-50 px-4 py-3 border-b border-orange-200">
                <div className="flex items-center">
                  <div className="w-6 h-4 bg-orange-500 rounded-sm mr-3"></div>
                  <h5 className="font-semibold text-gray-900">India - Required Formalities</h5>
                </div>
              </div>
              
              <div className="p-4 space-y-4">
                <div className="grid grid-cols-1 gap-4">
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h6 className="text-sm font-medium text-gray-700">Stamp Duty</h6>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        analysisData.formalitiesComparison.india.stampDuty.required 
                          ? 'bg-red-100 text-red-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {analysisData.formalitiesComparison.india.stampDuty.required ? 'Required' : 'Not Required'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{analysisData.formalitiesComparison.india.stampDuty.amount}</p>
                    <div className="text-xs text-gray-500">
                      <p className="font-medium mb-1">Exemptions:</p>
                      <ul className="space-y-1">
                        {analysisData.formalitiesComparison.india.stampDuty.exemptions.map((exemption, index) => (
                          <li key={index}>• {exemption}</li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  <div className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h6 className="text-sm font-medium text-gray-700">Registration</h6>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        analysisData.formalitiesComparison.india.registration.required 
                          ? 'bg-red-100 text-red-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {analysisData.formalitiesComparison.india.registration.required ? 'Required' : 'Optional'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">Authority: {analysisData.formalitiesComparison.india.registration.authority}</p>
                    <p className="text-sm text-gray-600">Timeline: {analysisData.formalitiesComparison.india.registration.timeline}</p>
                  </div>

                  <div className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h6 className="text-sm font-medium text-gray-700">Witnesses</h6>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        analysisData.formalitiesComparison.india.witnesses.required 
                          ? 'bg-red-100 text-red-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {analysisData.formalitiesComparison.india.witnesses.required ? 'Required' : 'Not Required'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">Count: {analysisData.formalitiesComparison.india.witnesses.count}</p>
                    <div className="text-xs text-gray-500">
                      <p className="font-medium mb-1">Requirements:</p>
                      <ul className="space-y-1">
                        {analysisData.formalitiesComparison.india.witnesses.requirements.map((req, index) => (
                          <li key={index}>• {req}</li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  <div className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h6 className="text-sm font-medium text-gray-700">Notarization</h6>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        analysisData.formalitiesComparison.india.notarization.required 
                          ? 'bg-red-100 text-red-800' 
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {analysisData.formalitiesComparison.india.notarization.required ? 'Required' : 'Recommended'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">{analysisData.formalitiesComparison.india.notarization.type}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* USA Formalities */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div className="bg-blue-50 px-4 py-3 border-b border-blue-200">
                <div className="flex items-center">
                  <div className="w-6 h-4 bg-blue-500 rounded-sm mr-3"></div>
                  <h5 className="font-semibold text-gray-900">USA - Required Formalities</h5>
                </div>
              </div>
              
              <div className="p-4 space-y-4">
                <div className="grid grid-cols-1 gap-4">
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h6 className="text-sm font-medium text-gray-700">Notarization</h6>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        analysisData.formalitiesComparison.usa.notarization.required 
                          ? 'bg-red-100 text-red-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {analysisData.formalitiesComparison.usa.notarization.required ? 'Required' : 'Not Required'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">Type: {analysisData.formalitiesComparison.usa.notarization.type}</p>
                    <div className="text-xs text-gray-500">
                      <p className="font-medium mb-1">State Requirements:</p>
                      <ul className="space-y-1">
                        {analysisData.formalitiesComparison.usa.notarization.stateRequirements.map((req, index) => (
                          <li key={index}>• {req}</li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  <div className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h6 className="text-sm font-medium text-gray-700">Witnesses</h6>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        analysisData.formalitiesComparison.usa.witnesses.required 
                          ? 'bg-red-100 text-red-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {analysisData.formalitiesComparison.usa.witnesses.required ? 'Required' : 'Not Required'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">Count: {analysisData.formalitiesComparison.usa.witnesses.count}</p>
                    <div className="text-xs text-gray-500">
                      <p className="font-medium mb-1">Requirements:</p>
                      <ul className="space-y-1">
                        {analysisData.formalitiesComparison.usa.witnesses.requirements.map((req, index) => (
                          <li key={index}>• {req}</li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  <div className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h6 className="text-sm font-medium text-gray-700">Recording</h6>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        analysisData.formalitiesComparison.usa.recording.required 
                          ? 'bg-red-100 text-red-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {analysisData.formalitiesComparison.usa.recording.required ? 'Required' : 'Optional'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">Authority: {analysisData.formalitiesComparison.usa.recording.authority}</p>
                    <p className="text-sm text-gray-600">Fees: {analysisData.formalitiesComparison.usa.recording.fees}</p>
                  </div>

                  <div className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h6 className="text-sm font-medium text-gray-700">Acknowledgment</h6>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        analysisData.formalitiesComparison.usa.acknowledgment.required 
                          ? 'bg-red-100 text-red-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {analysisData.formalitiesComparison.usa.acknowledgment.required ? 'Required' : 'Not Required'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">{analysisData.formalitiesComparison.usa.acknowledgment.type}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Key Differences */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h5 className="font-medium text-yellow-800 mb-3">Key Differences</h5>
            <ul className="space-y-2">
              {analysisData.formalitiesComparison.differences.map((difference, index) => (
                <li key={index} className="flex items-start text-sm text-yellow-700">
                  <svg className="w-4 h-4 text-yellow-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  {difference}
                </li>
              ))}
            </ul>
          </div>

          {/* Recommendations */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h5 className="font-medium text-blue-800 mb-3">Formalities Recommendations</h5>
            <ul className="space-y-2">
              {analysisData.formalitiesComparison.recommendations.map((recommendation, index) => (
                <li key={index} className="flex items-start text-sm text-blue-700">
                  <svg className="w-4 h-4 text-blue-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                  </svg>
                  {recommendation}
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <div className="max-w-sm mx-auto">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No Formalities Comparison Available</h3>
            <p className="mt-1 text-sm text-gray-500">Perform analysis to view detailed formalities comparison between jurisdictions.</p>
          </div>
        </div>
      )}
    </div>
  );

  const renderTaxImplications = () => (
    <div className="space-y-6">
      <h4 className="font-medium text-gray-900">Tax Implications Comparison</h4>
      
      {analysisData?.taxImplications ? (
        <div className="space-y-6">
          {/* Comparison Summary */}
          <div className="bg-gradient-to-r from-blue-50 to-orange-50 border border-gray-200 rounded-lg p-4">
            <h5 className="font-medium text-gray-900 mb-2">Tax Comparison Summary</h5>
            <p className="text-sm text-gray-700">{analysisData.taxImplications.comparisonSummary}</p>
            {analysisData.taxImplications.recommendedStructure && (
              <div className="mt-3 p-3 bg-white rounded border">
                <p className="text-sm font-medium text-gray-700 mb-1">Recommended Structure:</p>
                <p className="text-sm text-gray-600">{analysisData.taxImplications.recommendedStructure}</p>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* India Tax Implications */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div className="bg-orange-50 px-4 py-3 border-b border-orange-200">
                <div className="flex items-center">
                  <div className="w-6 h-4 bg-orange-500 rounded-sm mr-3"></div>
                  <h5 className="font-semibold text-gray-900">India - Tax Implications</h5>
                </div>
              </div>
              
              <div className="p-4">
                <ul className="space-y-3">
                  {analysisData.taxImplications.indiaImplications.map((implication, index) => (
                    <li key={index} className="flex items-start text-sm text-gray-600">
                      <div className="w-2 h-2 bg-orange-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                      <div>
                        <p>{implication}</p>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* USA Tax Implications */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div className="bg-blue-50 px-4 py-3 border-b border-blue-200">
                <div className="flex items-center">
                  <div className="w-6 h-4 bg-blue-500 rounded-sm mr-3"></div>
                  <h5 className="font-semibold text-gray-900">USA - Tax Implications</h5>
                </div>
              </div>
              
              <div className="p-4">
                <ul className="space-y-3">
                  {analysisData.taxImplications.usImplications.map((implication, index) => (
                    <li key={index} className="flex items-start text-sm text-gray-600">
                      <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                      <div>
                        <p>{implication}</p>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* DTAA Considerations */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h5 className="font-medium text-green-800 mb-3">India-US Double Taxation Avoidance Agreement (DTAA)</h5>
            <ul className="space-y-2">
              {analysisData.taxImplications.dtaaConsiderations.map((consideration, index) => (
                <li key={index} className="flex items-start text-sm text-green-700">
                  <svg className="w-4 h-4 text-green-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  {consideration}
                </li>
              ))}
            </ul>
          </div>

          {/* Tax Planning Recommendations */}
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <h5 className="font-medium text-purple-800 mb-3">Tax Planning Recommendations</h5>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white rounded p-3 border">
                <h6 className="text-sm font-medium text-gray-700 mb-2">For Indian Entities</h6>
                <ul className="text-xs text-gray-600 space-y-1">
                  <li>• Obtain GST registration if turnover exceeds threshold</li>
                  <li>• Plan for TDS compliance on payments</li>
                  <li>• Consider FEMA approvals for foreign transactions</li>
                  <li>• Utilize DTAA benefits for reduced withholding</li>
                </ul>
              </div>
              <div className="bg-white rounded p-3 border">
                <h6 className="text-sm font-medium text-gray-700 mb-2">For US Entities</h6>
                <ul className="text-xs text-gray-600 space-y-1">
                  <li>• Consider state tax implications</li>
                  <li>• Plan for federal withholding requirements</li>
                  <li>• Evaluate sales tax obligations</li>
                  <li>• Ensure FATCA compliance</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <div className="max-w-sm mx-auto">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No Tax Analysis Available</h3>
            <p className="mt-1 text-sm text-gray-500">Perform analysis to view detailed tax implications comparison.</p>
          </div>
        </div>
      )}
    </div>
  );

  const renderRecommendations = () => (
    <div className="space-y-6">
      <h4 className="font-medium text-gray-900">Cross-Border Transaction Recommendations</h4>
      
      {analysisData ? (
        <div className="space-y-6">
          {/* Governing Law Recommendation */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h5 className="font-medium text-gray-900 mb-3">Recommended Governing Law</h5>
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded border">
              <div>
                <p className="font-medium text-blue-900">{analysisData.recommendedGoverningLaw}</p>
                <p className="text-sm text-blue-700 mt-1">Optimal choice for cross-border enforceability</p>
              </div>
              <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full font-medium">
                Recommended
              </span>
            </div>
          </div>

          {/* Dispute Resolution Recommendation */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h5 className="font-medium text-gray-900 mb-3">Dispute Resolution Mechanism</h5>
            <div className="flex items-center justify-between p-3 bg-green-50 rounded border">
              <div>
                <p className="font-medium text-green-900">{analysisData.disputeResolutionRecommendation}</p>
                <p className="text-sm text-green-700 mt-1">Neutral venue with expertise in India-US commercial disputes</p>
              </div>
              <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full font-medium">
                Recommended
              </span>
            </div>
          </div>

          {/* Compliance Gaps */}
          {analysisData.complianceGaps && analysisData.complianceGaps.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h5 className="font-medium text-gray-900 mb-4">Compliance Gaps Analysis</h5>
              <div className="space-y-3">
                {analysisData.complianceGaps.map((gap, index) => (
                  <div key={index} className={`p-3 rounded-lg border ${
                    gap.impact === 'high' ? 'bg-red-50 border-red-200' :
                    gap.impact === 'medium' ? 'bg-yellow-50 border-yellow-200' :
                    'bg-blue-50 border-blue-200'
                  }`}>
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className={`px-2 py-1 text-xs rounded-full font-medium ${
                            gap.jurisdiction === 'india' ? 'bg-orange-100 text-orange-800' : 'bg-blue-100 text-blue-800'
                          }`}>
                            {gap.jurisdiction.toUpperCase()}
                          </span>
                          <span className={`px-2 py-1 text-xs rounded-full font-medium ${
                            gap.impact === 'high' ? 'bg-red-100 text-red-800' :
                            gap.impact === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {gap.impact.toUpperCase()} IMPACT
                          </span>
                          <span className={`px-2 py-1 text-xs rounded-full font-medium ${
                            gap.status === 'missing' ? 'bg-red-100 text-red-800' :
                            gap.status === 'partial' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-orange-100 text-orange-800'
                          }`}>
                            {gap.status.toUpperCase()}
                          </span>
                        </div>
                        <h6 className="font-medium text-gray-900">{gap.requirement}</h6>
                        <p className="text-sm text-gray-600 mt-1">{gap.recommendation}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Implementation Roadmap */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h5 className="font-medium text-gray-900 mb-4">Implementation Roadmap</h5>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-medium">1</div>
                <div className="flex-1">
                  <h6 className="font-medium text-gray-900">Legal Structure Setup</h6>
                  <p className="text-sm text-gray-600 mt-1">Establish appropriate legal entities in both jurisdictions to optimize tax efficiency and compliance.</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-medium">2</div>
                <div className="flex-1">
                  <h6 className="font-medium text-gray-900">Compliance Framework</h6>
                  <p className="text-sm text-gray-600 mt-1">Address identified compliance gaps and establish ongoing monitoring procedures.</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-medium">3</div>
                <div className="flex-1">
                  <h6 className="font-medium text-gray-900">Documentation & Execution</h6>
                  <p className="text-sm text-gray-600 mt-1">Prepare agreements with recommended governing law and dispute resolution clauses.</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-medium">4</div>
                <div className="flex-1">
                  <h6 className="font-medium text-gray-900">Ongoing Monitoring</h6>
                  <p className="text-sm text-gray-600 mt-1">Establish regular review processes for regulatory changes and compliance updates.</p>
                </div>
              </div>
            </div>
          </div>

          {/* Key Success Factors */}
          <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-gray-200 rounded-lg p-4">
            <h5 className="font-medium text-gray-900 mb-3">Key Success Factors</h5>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <h6 className="text-sm font-medium text-gray-700">Legal Considerations</h6>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Engage qualified counsel in both jurisdictions</li>
                  <li>• Regular review of regulatory changes</li>
                  <li>• Maintain comprehensive documentation</li>
                  <li>• Establish clear dispute resolution procedures</li>
                </ul>
              </div>
              <div className="space-y-2">
                <h6 className="text-sm font-medium text-gray-700">Business Considerations</h6>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Optimize tax structure across jurisdictions</li>
                  <li>• Ensure operational compliance</li>
                  <li>• Plan for currency and regulatory risks</li>
                  <li>• Maintain stakeholder communication</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <div className="max-w-sm mx-auto">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No Recommendations Available</h3>
            <p className="mt-1 text-sm text-gray-500">Perform analysis to view cross-border transaction recommendations.</p>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Cross-Border Jurisdiction Comparison</h3>
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-orange-500 rounded-sm mr-1"></div>
            <span>India</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-blue-500 rounded-sm mr-1"></div>
            <span>USA</span>
          </div>
        </div>
      </div>

      {/* Section Navigation */}
      <div className="flex space-x-1 mb-6 border-b">
        {[
          { key: 'enforceability', label: 'Enforceability' },
          { key: 'formalities', label: 'Formalities' },
          { key: 'tax', label: 'Tax Implications' },
          { key: 'recommendations', label: 'Recommendations' }
        ].map((section) => (
          <button
            key={section.key}
            onClick={() => setActiveSection(section.key as any)}
            className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
              activeSection === section.key
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            {section.label}
          </button>
        ))}
      </div>

      {/* Section Content */}
      <div className="min-h-[400px]">
        {activeSection === 'enforceability' && renderEnforceabilityComparison()}
        {activeSection === 'formalities' && renderFormalitiesComparison()}
        {activeSection === 'tax' && renderTaxImplications()}
        {activeSection === 'recommendations' && renderRecommendations()}
      </div>
    </div>
  );
};

export default JurisdictionComparison;