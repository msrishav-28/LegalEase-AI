'use client';

import React, { useState, useEffect } from 'react';
import { USLegalAnalysis as USAnalysisType, FederalLawReference, UCCAnalysis, SecuritiesAnalysis, PrivacyAnalysis, ChoiceOfLawAnalysis, ArbitrationAnalysis } from '@/types';

interface USLegalAnalysisProps {
  documentId?: string;
  analysis?: USAnalysisType;
  selectedState?: string;
  onAnalysisUpdate?: (analysis: USAnalysisType) => void;
  className?: string;
}

const FEDERAL_LAWS = [
  'United States Code (USC)',
  'Code of Federal Regulations (CFR)',
  'Securities Act of 1933',
  'Securities Exchange Act of 1934',
  'Investment Company Act of 1940',
  'Investment Advisers Act of 1940',
  'Sarbanes-Oxley Act of 2002',
  'Dodd-Frank Act',
  'California Consumer Privacy Act (CCPA)',
  'General Data Protection Regulation (GDPR)'
];

const UCC_ARTICLES = [
  'Article 1 - General Provisions',
  'Article 2 - Sales',
  'Article 2A - Leases',
  'Article 3 - Negotiable Instruments',
  'Article 4 - Bank Deposits',
  'Article 4A - Funds Transfers',
  'Article 5 - Letters of Credit',
  'Article 6 - Bulk Transfers',
  'Article 7 - Warehouse Receipts',
  'Article 8 - Investment Securities',
  'Article 9 - Secured Transactions'
];

export const USLegalAnalysis: React.FC<USLegalAnalysisProps> = ({
  documentId,
  analysis,
  selectedState = 'California',
  onAnalysisUpdate,
  className = ''
}) => {
  const [activeSection, setActiveSection] = useState<'federal' | 'ucc' | 'securities' | 'privacy' | 'choice-of-law' | 'arbitration'>('federal');
  const [isLoading, setIsLoading] = useState(false);
  const [analysisData, setAnalysisData] = useState<USAnalysisType | null>(analysis || null);

  useEffect(() => {
    if (analysis) {
      setAnalysisData(analysis);
    }
  }, [analysis]);

  const performAnalysis = async () => {
    if (!documentId) return;
    
    setIsLoading(true);
    try {
      // This would call the backend API for US legal analysis
      // const response = await api.post(`/api/jurisdiction/usa/analyze`, { 
      //   documentId, 
      //   state: selectedState 
      // });
      
      // Mock analysis data
      const mockAnalysis: USAnalysisType = {
        federalReferences: [
          {
            law: 'United States Code (USC)',
            section: '15 USC § 1',
            relevance: 'Federal antitrust laws applicable to commercial agreements'
          },
          {
            law: 'Securities Act of 1933',
            section: 'Section 5',
            relevance: 'Registration requirements for securities offerings'
          }
        ],
        stateJurisdiction: selectedState,
        uccAnalysis: {
          applicable: true,
          articles: ['Article 2 - Sales', 'Article 9 - Secured Transactions'],
          implications: [
            'UCC Article 2 governs sale of goods provisions',
            'Secured transaction rules apply to collateral arrangements',
            'State-specific UCC variations may apply'
          ]
        },
        securitiesCompliance: {
          applicable: true,
          regulations: ['Rule 506(b)', 'Rule 144A'],
          compliance: [
            'Private placement exemption available',
            'Accredited investor requirements must be met',
            'Form D filing required within 15 days'
          ]
        },
        privacyCompliance: {
          ccpaApplicable: selectedState === 'California',
          gdprApplicable: false,
          requirements: [
            'Consumer right to know about data collection',
            'Right to delete personal information',
            'Opt-out of sale of personal information'
          ],
          complianceChecklist: [
            { item: 'Privacy policy updated and accessible', completed: false, required: true },
            { item: 'Data processing agreements in place', completed: false, required: true },
            { item: 'Consumer request procedures established', completed: false, required: true },
            { item: 'Data breach response plan ready', completed: false, required: true }
          ]
        },
        choiceOfLawAnalysis: {
          currentGoverningLaw: 'Delaware Law',
          recommendedGoverningLaw: `${selectedState} Law`,
          enforceabilityFactors: [
            'Strong judicial system and precedent',
            'Business-friendly legal environment',
            'Established commercial law framework'
          ],
          conflictOfLawsIssues: [
            'Multi-state transaction considerations',
            'Federal vs state law preemption issues',
            'International enforcement challenges'
          ],
          recommendations: [
            `Consider ${selectedState} law for consistency with business operations`,
            'Include specific jurisdiction clause for dispute resolution',
            'Address federal law preemption where applicable'
          ]
        },
        arbitrationAnalysis: {
          hasArbitrationClause: true,
          arbitrationRules: 'AAA Commercial Arbitration Rules',
          seat: 'New York, NY',
          enforceabilityAssessment: 'Highly enforceable under Federal Arbitration Act',
          recommendations: [
            'Arbitration clause is well-drafted and enforceable',
            'Consider expedited procedures for smaller disputes',
            'Ensure arbitrator qualifications are specified'
          ],
          alternativeDispute: [
            'Mediation as first step before arbitration',
            'Expert determination for technical disputes',
            'Negotiation period before formal proceedings'
          ]
        }
      };
      
      setAnalysisData(mockAnalysis);
      onAnalysisUpdate?.(mockAnalysis);
    } catch (error) {
      console.error('Failed to perform US legal analysis:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderFederalReferences = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="font-medium text-gray-900">Federal Law References</h4>
        <button
          onClick={performAnalysis}
          disabled={isLoading}
          className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {isLoading ? 'Analyzing...' : 'Analyze'}
        </button>
      </div>
      
      {analysisData?.federalReferences ? (
        <div className="space-y-3">
          {analysisData.federalReferences.map((ref, index) => (
            <div key={index} className="p-4 bg-white border border-gray-200 rounded-lg">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h5 className="font-medium text-gray-900">{ref.law}</h5>
                  <p className="text-sm text-blue-600 mt-1">{ref.section}</p>
                  <p className="text-sm text-gray-600 mt-2">{ref.relevance}</p>
                </div>
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                  Federal
                </span>
              </div>
            </div>
          ))}
          
          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h5 className="text-sm font-medium text-yellow-800">State Law Considerations</h5>
                <p className="text-sm text-yellow-700 mt-1">
                  {selectedState} state laws may also apply. Consider consulting local counsel for state-specific requirements.
                </p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          Click "Analyze" to identify applicable federal laws
        </div>
      )}
    </div>
  );

  const renderUCCAnalysis = () => (
    <div className="space-y-4">
      <h4 className="font-medium text-gray-900">Uniform Commercial Code (UCC) Analysis</h4>
      
      {analysisData?.uccAnalysis ? (
        <div className="space-y-4">
          <div className="p-4 bg-white border border-gray-200 rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <span className="font-medium text-gray-900">UCC Applicability</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                analysisData.uccAnalysis.applicable 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {analysisData.uccAnalysis.applicable ? 'Applicable' : 'Not Applicable'}
              </span>
            </div>
            
            {analysisData.uccAnalysis.applicable && (
              <>
                <div className="mb-4">
                  <h6 className="text-sm font-medium text-gray-700 mb-2">Relevant UCC Articles:</h6>
                  <div className="space-y-2">
                    {analysisData.uccAnalysis.articles.map((article, index) => (
                      <div key={index} className="flex items-center p-2 bg-blue-50 rounded">
                        <svg className="h-4 w-4 text-blue-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                        <span className="text-sm text-gray-700">{article}</span>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h6 className="text-sm font-medium text-gray-700 mb-2">Key Implications:</h6>
                  <ul className="space-y-1">
                    {analysisData.uccAnalysis.implications.map((implication, index) => (
                      <li key={index} className="text-sm text-gray-600 flex items-start">
                        <span className="w-2 h-2 bg-blue-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                        {implication}
                      </li>
                    ))}
                  </ul>
                </div>
              </>
            )}
          </div>
          
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h6 className="text-sm font-medium text-blue-800 mb-2">UCC Best Practices</h6>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• Ensure clear identification of goods vs. services</li>
              <li>• Include specific performance terms and conditions</li>
              <li>• Address risk of loss and title transfer provisions</li>
              <li>• Consider warranty disclaimers and limitations</li>
            </ul>
          </div>
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          Perform analysis to view UCC applicability
        </div>
      )}
    </div>
  );

  const renderSecuritiesCompliance = () => (
    <div className="space-y-4">
      <h4 className="font-medium text-gray-900">Securities Law Compliance</h4>
      
      {analysisData?.securitiesCompliance ? (
        <div className="space-y-4">
          <div className="p-4 bg-white border border-gray-200 rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <span className="font-medium text-gray-900">Securities Laws Applicable</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                analysisData.securitiesCompliance.applicable 
                  ? 'bg-red-100 text-red-800' 
                  : 'bg-green-100 text-green-800'
              }`}>
                {analysisData.securitiesCompliance.applicable ? 'Applicable' : 'Not Applicable'}
              </span>
            </div>
            
            {analysisData.securitiesCompliance.applicable && (
              <>
                <div className="mb-4">
                  <h6 className="text-sm font-medium text-gray-700 mb-2">Relevant Regulations:</h6>
                  <div className="flex flex-wrap gap-2">
                    {analysisData.securitiesCompliance.regulations.map((regulation, index) => (
                      <span key={index} className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">
                        {regulation}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h6 className="text-sm font-medium text-gray-700 mb-2">Compliance Requirements:</h6>
                  <ul className="space-y-2">
                    {analysisData.securitiesCompliance.compliance.map((requirement, index) => (
                      <li key={index} className="text-sm text-gray-600 flex items-start">
                        <svg className="h-4 w-4 text-red-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                        </svg>
                        {requirement}
                      </li>
                    ))}
                  </ul>
                </div>
              </>
            )}
          </div>
          
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h5 className="text-sm font-medium text-red-800">Securities Law Warning</h5>
                <p className="text-sm text-red-700 mt-1">
                  Securities law violations can result in severe penalties. Consult with securities counsel before proceeding.
                </p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          Perform analysis to view securities compliance requirements
        </div>
      )}
    </div>
  );

  const renderChoiceOfLawAnalysis = () => (
    <div className="space-y-4">
      <h4 className="font-medium text-gray-900">Choice of Law Analysis</h4>
      
      {analysisData?.choiceOfLawAnalysis ? (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-white border border-gray-200 rounded-lg">
              <h5 className="font-medium text-gray-900 mb-3">Current Governing Law</h5>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">
                  {analysisData.choiceOfLawAnalysis.currentGoverningLaw || 'Not specified'}
                </span>
                {analysisData.choiceOfLawAnalysis.currentGoverningLaw && (
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                    Current
                  </span>
                )}
              </div>
            </div>
            
            <div className="p-4 bg-white border border-gray-200 rounded-lg">
              <h5 className="font-medium text-gray-900 mb-3">Recommended Governing Law</h5>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">
                  {analysisData.choiceOfLawAnalysis.recommendedGoverningLaw}
                </span>
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                  Recommended
                </span>
              </div>
            </div>
          </div>
          
          <div className="p-4 bg-white border border-gray-200 rounded-lg">
            <h5 className="font-medium text-gray-900 mb-3">Enforceability Factors</h5>
            <ul className="space-y-2">
              {analysisData.choiceOfLawAnalysis.enforceabilityFactors.map((factor, index) => (
                <li key={index} className="text-sm text-gray-600 flex items-start">
                  <svg className="h-4 w-4 text-green-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  {factor}
                </li>
              ))}
            </ul>
          </div>
          
          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <h5 className="font-medium text-yellow-800 mb-3">Conflict of Laws Issues</h5>
            <ul className="space-y-2">
              {analysisData.choiceOfLawAnalysis.conflictOfLawsIssues.map((issue, index) => (
                <li key={index} className="text-sm text-yellow-700 flex items-start">
                  <svg className="h-4 w-4 text-yellow-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  {issue}
                </li>
              ))}
            </ul>
          </div>
          
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h5 className="font-medium text-blue-800 mb-3">Recommendations</h5>
            <ul className="space-y-2">
              {analysisData.choiceOfLawAnalysis.recommendations.map((recommendation, index) => (
                <li key={index} className="text-sm text-blue-700 flex items-start">
                  <svg className="h-4 w-4 text-blue-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                  </svg>
                  {recommendation}
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          Perform analysis to view choice of law recommendations
        </div>
      )}
    </div>
  );

  const renderArbitrationAnalysis = () => (
    <div className="space-y-4">
      <h4 className="font-medium text-gray-900">Arbitration Clause Analysis</h4>
      
      {analysisData?.arbitrationAnalysis ? (
        <div className="space-y-4">
          <div className="p-4 bg-white border border-gray-200 rounded-lg">
            <div className="flex items-center justify-between mb-4">
              <h5 className="font-medium text-gray-900">Arbitration Clause Present</h5>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                analysisData.arbitrationAnalysis.hasArbitrationClause 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {analysisData.arbitrationAnalysis.hasArbitrationClause ? 'Yes' : 'No'}
              </span>
            </div>
            
            {analysisData.arbitrationAnalysis.hasArbitrationClause && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h6 className="text-sm font-medium text-gray-700 mb-2">Arbitration Rules</h6>
                  <p className="text-sm text-gray-600">
                    {analysisData.arbitrationAnalysis.arbitrationRules || 'Not specified'}
                  </p>
                </div>
                <div>
                  <h6 className="text-sm font-medium text-gray-700 mb-2">Seat of Arbitration</h6>
                  <p className="text-sm text-gray-600">
                    {analysisData.arbitrationAnalysis.seat || 'Not specified'}
                  </p>
                </div>
              </div>
            )}
          </div>
          
          <div className="p-4 bg-white border border-gray-200 rounded-lg">
            <h5 className="font-medium text-gray-900 mb-3">Enforceability Assessment</h5>
            <div className="p-3 bg-green-50 border border-green-200 rounded">
              <p className="text-sm text-green-700">
                {analysisData.arbitrationAnalysis.enforceabilityAssessment}
              </p>
            </div>
          </div>
          
          <div className="p-4 bg-white border border-gray-200 rounded-lg">
            <h5 className="font-medium text-gray-900 mb-3">Recommendations</h5>
            <ul className="space-y-2">
              {analysisData.arbitrationAnalysis.recommendations.map((recommendation, index) => (
                <li key={index} className="text-sm text-gray-600 flex items-start">
                  <svg className="h-4 w-4 text-blue-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  {recommendation}
                </li>
              ))}
            </ul>
          </div>
          
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h5 className="font-medium text-blue-800 mb-3">Alternative Dispute Resolution Options</h5>
            <ul className="space-y-2">
              {analysisData.arbitrationAnalysis.alternativeDispute.map((option, index) => (
                <li key={index} className="text-sm text-blue-700 flex items-start">
                  <svg className="h-4 w-4 text-blue-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                  </svg>
                  {option}
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          Perform analysis to view arbitration clause assessment
        </div>
      )}
    </div>
  );

  const renderPrivacyCompliance = () => (
    <div className="space-y-4">
      <h4 className="font-medium text-gray-900">Privacy Law Compliance</h4>
      
      {analysisData?.privacyCompliance ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-white border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <h5 className="font-medium text-gray-900">CCPA Compliance</h5>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  analysisData.privacyCompliance.ccpaApplicable 
                    ? 'bg-blue-100 text-blue-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {analysisData.privacyCompliance.ccpaApplicable ? 'Applicable' : 'Not Applicable'}
                </span>
              </div>
              {analysisData.privacyCompliance.ccpaApplicable && (
                <ul className="text-sm text-gray-600 space-y-2">
                  {analysisData.privacyCompliance.requirements.map((requirement, index) => (
                    <li key={index} className="flex items-start">
                      <svg className="h-4 w-4 text-green-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      {requirement}
                    </li>
                  ))}
                </ul>
              )}
            </div>
            
            <div className="p-4 bg-white border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <h5 className="font-medium text-gray-900">GDPR Considerations</h5>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  analysisData.privacyCompliance.gdprApplicable 
                    ? 'bg-purple-100 text-purple-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {analysisData.privacyCompliance.gdprApplicable ? 'Applicable' : 'Not Applicable'}
                </span>
              </div>
              <ul className="text-sm text-gray-600 space-y-2">
                <li className="flex items-start">
                  <svg className="h-4 w-4 text-purple-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  Lawful basis for processing required
                </li>
                <li className="flex items-start">
                  <svg className="h-4 w-4 text-purple-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  Data subject rights must be honored
                </li>
                <li className="flex items-start">
                  <svg className="h-4 w-4 text-purple-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  Cross-border transfer restrictions
                </li>
              </ul>
            </div>
          </div>
          
          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <h6 className="text-sm font-medium text-yellow-800 mb-2">Privacy Compliance Checklist</h6>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {analysisData.privacyCompliance.complianceChecklist.map((item, index) => (
                <label key={index} className="flex items-center text-sm text-yellow-700">
                  <input 
                    type="checkbox" 
                    className="mr-2" 
                    defaultChecked={item.completed}
                    disabled={!item.required}
                  />
                  {item.item}
                  {item.required && <span className="text-red-500 ml-1">*</span>}
                </label>
              ))}
            </div>
          </div>
        </>
      ) : (
        <div className="text-center py-8 text-gray-500">
          Perform analysis to view privacy compliance requirements
        </div>
      )}
    </div>
  );

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">US Legal Analysis</h3>
        <div className="text-sm text-gray-600">
          State: <span className="font-medium">{selectedState}</span>
        </div>
      </div>

      {/* Section Navigation */}
      <div className="flex space-x-1 mb-6 border-b">
        {[
          { key: 'federal', label: 'Federal Law' },
          { key: 'ucc', label: 'UCC Analysis' },
          { key: 'securities', label: 'Securities' },
          { key: 'privacy', label: 'Privacy Law' },
          { key: 'choice-of-law', label: 'Choice of Law' },
          { key: 'arbitration', label: 'Arbitration' }
        ].map((section) => (
          <button
            key={section.key}
            onClick={() => setActiveSection(section.key as any)}
            className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
              activeSection === section.key
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {section.label}
          </button>
        ))}
      </div>

      {/* Section Content */}
      <div className="min-h-[400px]">
        {activeSection === 'federal' && renderFederalReferences()}
        {activeSection === 'ucc' && renderUCCAnalysis()}
        {activeSection === 'securities' && renderSecuritiesCompliance()}
        {activeSection === 'privacy' && renderPrivacyCompliance()}
        {activeSection === 'choice-of-law' && renderChoiceOfLawAnalysis()}
        {activeSection === 'arbitration' && renderArbitrationAnalysis()}
      </div>
    </div>
  );
};

export default USLegalAnalysis;