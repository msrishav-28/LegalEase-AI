'use client';

import React, { useState, useEffect } from 'react';
import { IndianLegalAnalysis as IndianAnalysisType, ActReference, StampDutyAnalysis, GSTAnalysis, RegistrationRequirement } from '@/types';

interface IndianLegalAnalysisProps {
  documentId?: string;
  analysis?: IndianAnalysisType;
  selectedState?: string;
  onAnalysisUpdate?: (analysis: IndianAnalysisType) => void;
  onStateChange?: (state: string) => void;
  className?: string;
}

const INDIAN_STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat',
  'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh',
  'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
  'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh',
  'Uttarakhand', 'West Bengal', 'Delhi', 'Jammu and Kashmir', 'Ladakh'
];

const INDIAN_ACTS = [
  {
    name: 'Indian Contract Act, 1872',
    sections: ['Section 10 - What agreements are contracts', 'Section 23 - Lawful consideration', 'Section 73 - Compensation for loss'],
    applicability: 'All contracts and agreements'
  },
  {
    name: 'Companies Act, 2013',
    sections: ['Section 2(20) - Definition of company', 'Section 179 - Powers of Board', 'Section 188 - Related party transactions'],
    applicability: 'Corporate agreements and transactions'
  },
  {
    name: 'Goods and Services Tax Act, 2017',
    sections: ['Section 2(52) - Goods', 'Section 2(102) - Services', 'Section 9 - Levy and collection'],
    applicability: 'Supply of goods and services'
  },
  {
    name: 'Income Tax Act, 1961',
    sections: ['Section 194C - TDS on contracts', 'Section 40(a)(ia) - Disallowance', 'Section 206AA - Higher TDS'],
    applicability: 'Tax implications of contracts'
  },
  {
    name: 'Foreign Exchange Management Act, 1999',
    sections: ['Section 3 - Dealing in foreign exchange', 'Section 5 - Holding of foreign exchange', 'Section 6 - Current account transactions'],
    applicability: 'Foreign exchange transactions'
  },
  {
    name: 'Indian Partnership Act, 1932',
    sections: ['Section 4 - Definition of partnership', 'Section 11 - Extent of partner\'s liability', 'Section 18 - Rights and duties'],
    applicability: 'Partnership agreements'
  },
  {
    name: 'Sale of Goods Act, 1930',
    sections: ['Section 4 - Sale and agreement to sell', 'Section 12 - Conditions and warranties', 'Section 39 - Unpaid seller'],
    applicability: 'Sale and purchase agreements'
  },
  {
    name: 'Negotiable Instruments Act, 1881',
    sections: ['Section 13 - Negotiable instrument', 'Section 138 - Dishonour of cheque', 'Section 147 - Presumption'],
    applicability: 'Payment instruments and guarantees'
  }
];

const STAMP_DUTY_RATES = {
  'Maharashtra': { 
    agreement: { fixed: 100, percentage: 0.1, minimum: 100, maximum: 25000 },
    contract: { fixed: 200, percentage: 0.1, minimum: 200, maximum: 50000 },
    mou: { fixed: 100, percentage: 0.05, minimum: 100, maximum: 10000 },
    lease: { fixed: 500, percentage: 0.25, minimum: 500, maximum: 100000 },
    partnership: { fixed: 1000, percentage: 0.1, minimum: 1000, maximum: 50000 }
  },
  'Delhi': { 
    agreement: { fixed: 100, percentage: 0.1, minimum: 100, maximum: 30000 },
    contract: { fixed: 200, percentage: 0.1, minimum: 200, maximum: 60000 },
    mou: { fixed: 100, percentage: 0.05, minimum: 100, maximum: 15000 },
    lease: { fixed: 500, percentage: 0.2, minimum: 500, maximum: 80000 },
    partnership: { fixed: 1000, percentage: 0.1, minimum: 1000, maximum: 40000 }
  },
  'Karnataka': { 
    agreement: { fixed: 100, percentage: 0.1, minimum: 100, maximum: 20000 },
    contract: { fixed: 200, percentage: 0.1, minimum: 200, maximum: 40000 },
    mou: { fixed: 100, percentage: 0.05, minimum: 100, maximum: 8000 },
    lease: { fixed: 500, percentage: 0.2, minimum: 500, maximum: 75000 },
    partnership: { fixed: 1000, percentage: 0.1, minimum: 1000, maximum: 35000 }
  },
  'Tamil Nadu': { 
    agreement: { fixed: 100, percentage: 0.1, minimum: 100, maximum: 22000 },
    contract: { fixed: 200, percentage: 0.1, minimum: 200, maximum: 45000 },
    mou: { fixed: 100, percentage: 0.05, minimum: 100, maximum: 12000 },
    lease: { fixed: 500, percentage: 0.25, minimum: 500, maximum: 90000 },
    partnership: { fixed: 1000, percentage: 0.1, minimum: 1000, maximum: 45000 }
  },
  'Gujarat': { 
    agreement: { fixed: 100, percentage: 0.1, minimum: 100, maximum: 18000 },
    contract: { fixed: 200, percentage: 0.1, minimum: 200, maximum: 35000 },
    mou: { fixed: 100, percentage: 0.05, minimum: 100, maximum: 7000 },
    lease: { fixed: 500, percentage: 0.2, minimum: 500, maximum: 70000 },
    partnership: { fixed: 1000, percentage: 0.1, minimum: 1000, maximum: 30000 }
  }
};

const GST_RATES = {
  'Legal Services': { rate: 18, hsn: '9991', exemptions: ['Services to government', 'Services below Rs. 20 lakhs turnover'] },
  'Consulting Services': { rate: 18, hsn: '9992', exemptions: ['Export of services', 'Services to SEZ'] },
  'Software Services': { rate: 18, hsn: '9983', exemptions: ['Export of services', 'Services to SEZ units'] },
  'Construction Services': { rate: 18, hsn: '9954', exemptions: ['Affordable housing', 'Government projects'] },
  'Financial Services': { rate: 18, hsn: '9971', exemptions: ['Services by RBI', 'Certain banking services'] }
};

interface ComplianceCheck {
  requirement: string;
  status: 'compliant' | 'non-compliant' | 'partial' | 'unknown';
  details: string;
  recommendation?: string;
}

export const IndianLegalAnalysis: React.FC<IndianLegalAnalysisProps> = ({
  documentId,
  analysis,
  selectedState = 'Maharashtra',
  onAnalysisUpdate,
  onStateChange,
  className = ''
}) => {
  const [activeSection, setActiveSection] = useState<'acts' | 'stamp-duty' | 'gst' | 'registration'>('acts');
  const [isLoading, setIsLoading] = useState(false);
  const [analysisData, setAnalysisData] = useState<IndianAnalysisType | null>(analysis || null);
  const [currentState, setCurrentState] = useState(selectedState);
  const [complianceChecks, setComplianceChecks] = useState<ComplianceCheck[]>([]);
  const [stampDutyCalculation, setStampDutyCalculation] = useState({
    documentType: 'agreement',
    documentValue: 0,
    calculatedDuty: 0,
    additionalCharges: 0,
    totalAmount: 0
  });
  const [gstCalculation, setGstCalculation] = useState({
    serviceType: 'Legal Services',
    serviceValue: 0,
    gstAmount: 0,
    totalAmount: 0,
    inputTaxCredit: false
  });

  useEffect(() => {
    if (analysis) {
      setAnalysisData(analysis);
    }
  }, [analysis]);

  useEffect(() => {
    setCurrentState(selectedState);
    calculateStampDuty();
  }, [selectedState]);

  const handleStateChange = (newState: string) => {
    setCurrentState(newState);
    onStateChange?.(newState);
    calculateStampDuty();
  };

  const performAnalysis = async () => {
    if (!documentId) return;
    
    setIsLoading(true);
    try {
      // This would call the backend API for Indian legal analysis
      // const response = await api.post(`/api/jurisdiction/india/analyze`, { 
      //   documentId, 
      //   state: currentState 
      // });
      
      // Enhanced mock analysis data with state-specific information
      const mockAnalysis: IndianAnalysisType = {
        actReferences: [
          {
            act: 'Indian Contract Act, 1872',
            section: 'Section 10',
            relevance: 'Defines what agreements are contracts - applicable to all contractual arrangements'
          },
          {
            act: 'Companies Act, 2013',
            section: 'Section 2(20)',
            relevance: 'Definition of company applicable to corporate agreements'
          },
          {
            act: 'Goods and Services Tax Act, 2017',
            section: 'Section 9',
            relevance: 'Levy and collection of GST on supply of services'
          }
        ],
        stampDuty: {
          state: currentState,
          amount: stampDutyCalculation.calculatedDuty,
          calculation: `Calculated based on ${currentState} stamp duty rates`,
          exemptions: getStateSpecificExemptions(currentState)
        },
        gstImplications: {
          applicable: true,
          rate: 18,
          implications: [
            'GST applicable on legal and consulting services at 18%',
            'Input tax credit available for registered businesses',
            'Reverse charge mechanism may apply for certain services',
            `State-specific compliance requirements for ${currentState}`
          ]
        },
        registrationRequirements: getStateSpecificRegistrationRequirements(currentState)
      };
      
      // Generate compliance checks
      const checks = generateComplianceChecks(mockAnalysis, currentState);
      setComplianceChecks(checks);
      
      setAnalysisData(mockAnalysis);
      onAnalysisUpdate?.(mockAnalysis);
    } catch (error) {
      console.error('Failed to perform Indian legal analysis:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStateSpecificExemptions = (state: string): string[] => {
    const commonExemptions = ['Government transactions', 'Charitable organizations'];
    const stateSpecific: Record<string, string[]> = {
      'Maharashtra': [...commonExemptions, 'Cooperative societies', 'Educational institutions'],
      'Delhi': [...commonExemptions, 'Startups registered under Startup India', 'Women entrepreneurs'],
      'Karnataka': [...commonExemptions, 'IT companies in SEZ', 'Agricultural cooperatives'],
      'Tamil Nadu': [...commonExemptions, 'Handloom cooperatives', 'Self-help groups'],
      'Gujarat': [...commonExemptions, 'Export-oriented units', 'Industrial cooperatives']
    };
    return stateSpecific[state] || commonExemptions;
  };

  const getStateSpecificRegistrationRequirements = (state: string): RegistrationRequirement[] => {
    const baseRequirements = [
      {
        type: 'Stamp Duty Payment',
        required: true,
        authority: 'State Revenue Department',
        timeline: 'Within 30 days of execution'
      }
    ];

    const stateSpecific: Record<string, RegistrationRequirement[]> = {
      'Maharashtra': [
        ...baseRequirements,
        {
          type: 'Registration with Sub-Registrar',
          required: false,
          authority: 'Sub-Registrar Office',
          timeline: 'Optional for agreements below Rs. 100'
        },
        {
          type: 'Maharashtra Shops and Establishments Act',
          required: true,
          authority: 'Labour Department',
          timeline: 'Within 30 days if establishing business'
        }
      ],
      'Delhi': [
        ...baseRequirements,
        {
          type: 'Delhi Shops and Establishments Act',
          required: true,
          authority: 'Labour Department',
          timeline: 'Within 30 days of commencement'
        }
      ]
    };

    return stateSpecific[state] || baseRequirements;
  };

  const generateComplianceChecks = (analysis: IndianAnalysisType, state: string): ComplianceCheck[] => {
    return [
      {
        requirement: 'Stamp Duty Compliance',
        status: analysis.stampDuty.amount > 0 ? 'compliant' : 'non-compliant',
        details: `Stamp duty of ₹${analysis.stampDuty.amount} calculated for ${state}`,
        recommendation: analysis.stampDuty.amount === 0 ? 'Ensure proper stamp duty payment' : undefined
      },
      {
        requirement: 'GST Registration',
        status: 'partial',
        details: 'GST registration required if annual turnover exceeds ₹20 lakhs',
        recommendation: 'Verify GST registration status of all parties'
      },
      {
        requirement: 'Contract Act Compliance',
        status: 'compliant',
        details: 'Agreement structure complies with Indian Contract Act, 1872'
      },
      {
        requirement: 'State-specific Requirements',
        status: 'unknown',
        details: `Additional ${state}-specific requirements may apply`,
        recommendation: 'Consult local legal counsel for state-specific compliance'
      }
    ];
  };

  const calculateStampDuty = () => {
    const rates = STAMP_DUTY_RATES[currentState as keyof typeof STAMP_DUTY_RATES] || STAMP_DUTY_RATES['Maharashtra'];
    const rateInfo = rates[stampDutyCalculation.documentType as keyof typeof rates];
    
    if (!rateInfo) return;
    
    let calculatedDuty = rateInfo.fixed;
    
    if (stampDutyCalculation.documentValue > 0) {
      // Calculate percentage-based duty
      const percentageDuty = (stampDutyCalculation.documentValue * rateInfo.percentage) / 100;
      calculatedDuty = Math.max(rateInfo.minimum, Math.min(percentageDuty, rateInfo.maximum));
    }
    
    // Additional charges (registration fees, etc.)
    const additionalCharges = calculatedDuty * 0.1; // 10% additional charges
    const totalAmount = calculatedDuty + additionalCharges;
    
    setStampDutyCalculation(prev => ({ 
      ...prev, 
      calculatedDuty,
      additionalCharges,
      totalAmount
    }));
  };

  const calculateGST = () => {
    const serviceInfo = GST_RATES[gstCalculation.serviceType as keyof typeof GST_RATES];
    if (!serviceInfo || gstCalculation.serviceValue <= 0) return;
    
    const gstAmount = (gstCalculation.serviceValue * serviceInfo.rate) / 100;
    const totalAmount = gstCalculation.serviceValue + gstAmount;
    
    setGstCalculation(prev => ({
      ...prev,
      gstAmount,
      totalAmount
    }));
  };

  useEffect(() => {
    calculateStampDuty();
  }, [stampDutyCalculation.documentType, stampDutyCalculation.documentValue, currentState]);

  useEffect(() => {
    calculateGST();
  }, [gstCalculation.serviceType, gstCalculation.serviceValue]);

  const renderActReferences = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h4 className="font-medium text-gray-900">Indian Acts Compliance Analysis</h4>
        <button
          onClick={performAnalysis}
          disabled={isLoading}
          className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {isLoading && (
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          )}
          <span>{isLoading ? 'Analyzing...' : 'Perform Analysis'}</span>
        </button>
      </div>

      {/* Compliance Overview */}
      {complianceChecks.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h5 className="font-medium text-gray-900 mb-3">Compliance Overview</h5>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {complianceChecks.map((check, index) => (
              <div key={index} className="bg-white rounded-lg p-3 border">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">{check.requirement}</span>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    check.status === 'compliant' ? 'bg-green-100 text-green-800' :
                    check.status === 'non-compliant' ? 'bg-red-100 text-red-800' :
                    check.status === 'partial' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {check.status}
                  </span>
                </div>
                <p className="text-xs text-gray-600">{check.details}</p>
                {check.recommendation && (
                  <p className="text-xs text-blue-600 mt-1 font-medium">{check.recommendation}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      
      {analysisData?.actReferences ? (
        <div className="space-y-4">
          {analysisData.actReferences.map((ref, index) => {
            const actInfo = INDIAN_ACTS.find(act => act.name === ref.act);
            return (
              <div key={index} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h5 className="font-semibold text-gray-900">{ref.act}</h5>
                      <p className="text-sm text-blue-600 mt-1 font-medium">{ref.section}</p>
                      <p className="text-sm text-gray-600 mt-2">{ref.relevance}</p>
                      
                      {actInfo && (
                        <div className="mt-3">
                          <p className="text-xs text-gray-500 mb-2">Applicability: {actInfo.applicability}</p>
                          <details className="text-sm">
                            <summary className="cursor-pointer text-blue-600 hover:text-blue-800">
                              View Related Sections
                            </summary>
                            <ul className="mt-2 space-y-1 text-xs text-gray-600 ml-4">
                              {actInfo.sections.map((section, idx) => (
                                <li key={idx} className="list-disc">{section}</li>
                              ))}
                            </ul>
                          </details>
                        </div>
                      )}
                    </div>
                    <div className="flex flex-col items-end space-y-2">
                      <span className="px-3 py-1 bg-green-100 text-green-800 text-xs rounded-full font-medium">
                        Applicable
                      </span>
                      <button className="text-xs text-blue-600 hover:text-blue-800">
                        View Full Text
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <div className="max-w-sm mx-auto">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No Analysis Available</h3>
            <p className="mt-1 text-sm text-gray-500">Click "Perform Analysis" to identify applicable Indian acts and compliance requirements.</p>
          </div>
        </div>
      )}
    </div>
  );

  const renderStampDutyCalculator = () => {
    const currentRates = STAMP_DUTY_RATES[currentState as keyof typeof STAMP_DUTY_RATES] || STAMP_DUTY_RATES['Maharashtra'];
    const currentRate = currentRates[stampDutyCalculation.documentType as keyof typeof currentRates];
    
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h4 className="font-medium text-gray-900">Stamp Duty Calculator</h4>
          <div className="text-sm text-gray-600">
            State: <span className="font-medium text-blue-600">{currentState}</span>
          </div>
        </div>
        
        {/* State Selection */}
        <div className="bg-gray-50 rounded-lg p-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select State for Calculation
          </label>
          <select
            value={currentState}
            onChange={(e) => handleStateChange(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white"
          >
            {INDIAN_STATES.map(state => (
              <option key={state} value={state}>{state}</option>
            ))}
          </select>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input Section */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Document Type
              </label>
              <select
                value={stampDutyCalculation.documentType}
                onChange={(e) => setStampDutyCalculation(prev => ({ ...prev, documentType: e.target.value }))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="agreement">Agreement</option>
                <option value="contract">Contract</option>
                <option value="mou">Memorandum of Understanding</option>
                <option value="lease">Lease Agreement</option>
                <option value="partnership">Partnership Deed</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Document Value (₹)
              </label>
              <input
                type="number"
                value={stampDutyCalculation.documentValue}
                onChange={(e) => setStampDutyCalculation(prev => ({ ...prev, documentValue: Number(e.target.value) }))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Enter document value"
                min="0"
              />
              <p className="text-xs text-gray-500 mt-1">
                Leave blank or enter 0 for fixed duty calculation
              </p>
            </div>

            {/* Rate Information */}
            {currentRate && (
              <div className="bg-blue-50 rounded-lg p-4">
                <h6 className="font-medium text-gray-900 mb-2">Rate Information for {currentState}</h6>
                <div className="text-sm space-y-1">
                  <p><span className="font-medium">Fixed Rate:</span> ₹{currentRate.fixed}</p>
                  <p><span className="font-medium">Percentage Rate:</span> {currentRate.percentage}%</p>
                  <p><span className="font-medium">Minimum:</span> ₹{currentRate.minimum}</p>
                  <p><span className="font-medium">Maximum:</span> ₹{currentRate.maximum}</p>
                </div>
              </div>
            )}
          </div>
          
          {/* Calculation Results */}
          <div className="space-y-4">
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h6 className="font-medium text-gray-900 mb-4">Calculation Breakdown</h6>
              
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Base Stamp Duty:</span>
                  <span className="font-medium">₹{stampDutyCalculation.calculatedDuty.toFixed(2)}</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Additional Charges (10%):</span>
                  <span className="font-medium">₹{stampDutyCalculation.additionalCharges.toFixed(2)}</span>
                </div>
                
                <hr className="border-gray-200" />
                
                <div className="flex justify-between items-center">
                  <span className="font-medium text-gray-900">Total Amount:</span>
                  <span className="text-xl font-bold text-blue-600">
                    ₹{stampDutyCalculation.totalAmount.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>

            {/* Payment Information */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h6 className="font-medium text-yellow-800 mb-2">Payment Information</h6>
              <ul className="text-sm text-yellow-700 space-y-1">
                <li>• Payment must be made within 30 days of document execution</li>
                <li>• Late payment attracts penalty of 2% per month</li>
                <li>• Payment can be made online through state revenue portal</li>
                <li>• Physical stamp paper can be purchased from authorized vendors</li>
              </ul>
            </div>
          </div>
        </div>
        
        {analysisData?.stampDuty && (
          <div className="bg-gray-50 rounded-lg p-4">
            <h5 className="font-medium text-gray-900 mb-3">Document Analysis Results</h5>
            <p className="text-sm text-gray-600 mb-3">{analysisData.stampDuty.calculation}</p>
            
            {analysisData.stampDuty.exemptions && (
              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">Available Exemptions:</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {analysisData.stampDuty.exemptions.map((exemption, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm text-gray-600">{exemption}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  const renderGSTAnalysis = () => {
    const currentGSTInfo = GST_RATES[gstCalculation.serviceType as keyof typeof GST_RATES];
    
    return (
      <div className="space-y-6">
        <h4 className="font-medium text-gray-900">GST Analysis & Compliance</h4>
        
        {/* GST Calculator */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h5 className="font-medium text-gray-900 mb-4">GST Calculator</h5>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Service Type
              </label>
              <select
                value={gstCalculation.serviceType}
                onChange={(e) => setGstCalculation(prev => ({ ...prev, serviceType: e.target.value }))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                {Object.keys(GST_RATES).map(service => (
                  <option key={service} value={service}>{service}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Service Value (₹)
              </label>
              <input
                type="number"
                value={gstCalculation.serviceValue}
                onChange={(e) => setGstCalculation(prev => ({ ...prev, serviceValue: Number(e.target.value) }))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Enter service value"
                min="0"
              />
            </div>
          </div>
          
          <div className="mt-4 flex items-center">
            <input
              type="checkbox"
              id="inputTaxCredit"
              checked={gstCalculation.inputTaxCredit}
              onChange={(e) => setGstCalculation(prev => ({ ...prev, inputTaxCredit: e.target.checked }))}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="inputTaxCredit" className="ml-2 text-sm text-gray-700">
              Input Tax Credit Available
            </label>
          </div>
          
          {currentGSTInfo && (
            <div className="mt-4 bg-white rounded-lg p-4 border">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-600">HSN/SAC Code</p>
                  <p className="font-medium">{currentGSTInfo.hsn}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">GST Rate</p>
                  <p className="font-medium">{currentGSTInfo.rate}%</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">GST Amount</p>
                  <p className="font-medium text-blue-600">₹{gstCalculation.gstAmount.toFixed(2)}</p>
                </div>
              </div>
              
              <div className="mt-4 pt-4 border-t">
                <div className="flex justify-between items-center">
                  <span className="font-medium">Total Amount (including GST):</span>
                  <span className="text-lg font-bold text-blue-600">₹{gstCalculation.totalAmount.toFixed(2)}</span>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {analysisData?.gstImplications ? (
          <div className="space-y-4">
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <span className="font-medium text-gray-900">GST Applicability Analysis</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  analysisData.gstImplications.applicable 
                    ? 'bg-orange-100 text-orange-800' 
                    : 'bg-green-100 text-green-800'
                }`}>
                  {analysisData.gstImplications.applicable ? 'GST Applicable' : 'GST Not Applicable'}
                </span>
              </div>
              
              {analysisData.gstImplications.applicable && analysisData.gstImplications.rate && (
                <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">Applicable GST Rate:</span>
                    <span className="font-bold text-blue-600">{analysisData.gstImplications.rate}%</span>
                  </div>
                </div>
              )}
              
              <div>
                <h6 className="text-sm font-medium text-gray-700 mb-3">GST Implications & Compliance:</h6>
                <div className="space-y-2">
                  {analysisData.gstImplications.implications.map((implication, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <div className="flex-shrink-0 w-5 h-5 bg-blue-100 rounded-full flex items-center justify-center mt-0.5">
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      </div>
                      <span className="text-sm text-gray-600">{implication}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* GST Exemptions */}
            {currentGSTInfo?.exemptions && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h6 className="font-medium text-green-800 mb-3">Available GST Exemptions</h6>
                <div className="space-y-2">
                  {currentGSTInfo.exemptions.map((exemption, index) => (
                    <div key={index} className="flex items-start space-x-2">
                      <svg className="w-4 h-4 text-green-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm text-green-700">{exemption}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Compliance Checklist */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h6 className="font-medium text-yellow-800 mb-3">GST Compliance Checklist</h6>
              <div className="space-y-2 text-sm text-yellow-700">
                <div className="flex items-center space-x-2">
                  <input type="checkbox" className="rounded" />
                  <span>Verify GST registration of all parties</span>
                </div>
                <div className="flex items-center space-x-2">
                  <input type="checkbox" className="rounded" />
                  <span>Ensure proper GST invoicing format</span>
                </div>
                <div className="flex items-center space-x-2">
                  <input type="checkbox" className="rounded" />
                  <span>Check reverse charge mechanism applicability</span>
                </div>
                <div className="flex items-center space-x-2">
                  <input type="checkbox" className="rounded" />
                  <span>Verify input tax credit eligibility</span>
                </div>
                <div className="flex items-center space-x-2">
                  <input type="checkbox" className="rounded" />
                  <span>Ensure timely GST return filing</span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <div className="max-w-sm mx-auto">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No GST Analysis Available</h3>
              <p className="mt-1 text-sm text-gray-500">Perform document analysis to view GST implications and compliance requirements.</p>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderRegistrationRequirements = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h4 className="font-medium text-gray-900">Registration Requirements & Compliance</h4>
        <div className="text-sm text-gray-600">
          State: <span className="font-medium text-blue-600">{currentState}</span>
        </div>
      </div>
      
      {analysisData?.registrationRequirements ? (
        <div className="space-y-4">
          {/* Requirements Overview */}
          <div className="bg-blue-50 rounded-lg p-4">
            <h5 className="font-medium text-blue-900 mb-3">Requirements Summary</h5>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {analysisData.registrationRequirements.filter(req => req.required).length}
                </div>
                <div className="text-sm text-gray-600">Mandatory</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">
                  {analysisData.registrationRequirements.filter(req => !req.required).length}
                </div>
                <div className="text-sm text-gray-600">Optional</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {analysisData.registrationRequirements.length}
                </div>
                <div className="text-sm text-gray-600">Total</div>
              </div>
            </div>
          </div>

          {/* Detailed Requirements */}
          <div className="space-y-4">
            {analysisData.registrationRequirements.map((requirement, index) => (
              <div key={index} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center mb-3">
                        <h5 className="font-semibold text-gray-900">{requirement.type}</h5>
                        <span className={`ml-3 px-3 py-1 text-xs rounded-full font-medium ${
                          requirement.required 
                            ? 'bg-red-100 text-red-800' 
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {requirement.required ? 'Mandatory' : 'Optional'}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div>
                          <p className="text-sm font-medium text-gray-700 mb-1">Responsible Authority</p>
                          <p className="text-sm text-gray-600">{requirement.authority}</p>
                        </div>
                        {requirement.timeline && (
                          <div>
                            <p className="text-sm font-medium text-gray-700 mb-1">Timeline</p>
                            <p className="text-sm text-gray-600">{requirement.timeline}</p>
                          </div>
                        )}
                      </div>

                      {/* Additional Information based on requirement type */}
                      {requirement.type.includes('Stamp Duty') && (
                        <div className="bg-yellow-50 rounded-lg p-3 mb-3">
                          <h6 className="font-medium text-yellow-800 mb-2">Stamp Duty Details</h6>
                          <ul className="text-sm text-yellow-700 space-y-1">
                            <li>• Can be paid online through state revenue portal</li>
                            <li>• Physical stamp paper available from authorized vendors</li>
                            <li>• Late payment attracts penalty of 2% per month</li>
                            <li>• E-stamping facility available in most states</li>
                          </ul>
                        </div>
                      )}

                      {requirement.type.includes('Registration') && (
                        <div className="bg-blue-50 rounded-lg p-3 mb-3">
                          <h6 className="font-medium text-blue-800 mb-2">Registration Process</h6>
                          <ul className="text-sm text-blue-700 space-y-1">
                            <li>• Submit application with required documents</li>
                            <li>• Pay registration fees as applicable</li>
                            <li>• Verification by registering authority</li>
                            <li>• Certificate issuance upon approval</li>
                          </ul>
                        </div>
                      )}

                      {requirement.type.includes('Shops and Establishments') && (
                        <div className="bg-green-50 rounded-lg p-3 mb-3">
                          <h6 className="font-medium text-green-800 mb-2">Shops & Establishments Act</h6>
                          <ul className="text-sm text-green-700 space-y-1">
                            <li>• Required for all commercial establishments</li>
                            <li>• Online registration available in most states</li>
                            <li>• Annual renewal required</li>
                            <li>• Display certificate at business premises</li>
                          </ul>
                        </div>
                      )}
                    </div>
                    
                    <div className="flex flex-col items-end space-y-2 ml-4">
                      <button className="text-xs text-blue-600 hover:text-blue-800 font-medium">
                        View Details
                      </button>
                      <button className="text-xs text-green-600 hover:text-green-800 font-medium">
                        Download Forms
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* State-specific Information */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h5 className="font-medium text-gray-900 mb-3">State-specific Information for {currentState}</h5>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h6 className="font-medium text-gray-700 mb-2">Online Portals</h6>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• State Revenue Department Portal</li>
                  <li>• Registrar Office Online Services</li>
                  <li>• Labour Department Portal</li>
                  <li>• Commercial Tax Department</li>
                </ul>
              </div>
              <div>
                <h6 className="font-medium text-gray-700 mb-2">Important Contacts</h6>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Sub-Registrar Office: Contact local office</li>
                  <li>• Revenue Department: State helpline</li>
                  <li>• Labour Department: Regional office</li>
                  <li>• Legal Aid: State legal services authority</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Compliance Timeline */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h5 className="font-medium text-gray-900 mb-4">Compliance Timeline</h5>
            <div className="space-y-3">
              {analysisData.registrationRequirements
                .filter(req => req.timeline)
                .sort((a, b) => {
                  // Sort by urgency (required first, then by timeline)
                  if (a.required && !b.required) return -1;
                  if (!a.required && b.required) return 1;
                  return 0;
                })
                .map((requirement, index) => (
                  <div key={index} className="flex items-center space-x-4">
                    <div className={`w-3 h-3 rounded-full ${
                      requirement.required ? 'bg-red-500' : 'bg-yellow-500'
                    }`}></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{requirement.type}</p>
                      <p className="text-xs text-gray-600">{requirement.timeline}</p>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      requirement.required 
                        ? 'bg-red-100 text-red-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {requirement.required ? 'Urgent' : 'Optional'}
                    </span>
                  </div>
                ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <div className="max-w-sm mx-auto">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No Registration Requirements Available</h3>
            <p className="mt-1 text-sm text-gray-500">Perform document analysis to view state-specific registration requirements and compliance information.</p>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className={`bg-white rounded-lg shadow-lg border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold">Indian Legal Analysis</h3>
            <p className="text-blue-100 text-sm mt-1">Comprehensive analysis for Indian jurisdiction</p>
          </div>
          <div className="text-right">
            <div className="text-sm text-blue-100">Selected State</div>
            <div className="font-semibold text-lg">{currentState}</div>
          </div>
        </div>
      </div>

      <div className="p-6">
        {/* Section Navigation */}
        <div className="flex flex-wrap gap-1 mb-6 border-b border-gray-200">
          {[
            { key: 'acts', label: 'Acts Compliance', icon: '📋' },
            { key: 'stamp-duty', label: 'Stamp Duty', icon: '💰' },
            { key: 'gst', label: 'GST Analysis', icon: '📊' },
            { key: 'registration', label: 'Registration', icon: '📝' }
          ].map((section) => (
            <button
              key={section.key}
              onClick={() => setActiveSection(section.key as any)}
              className={`flex items-center space-x-2 px-4 py-3 font-medium text-sm border-b-2 transition-all duration-200 ${
                activeSection === section.key
                  ? 'border-blue-500 text-blue-600 bg-blue-50'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              <span>{section.icon}</span>
              <span>{section.label}</span>
            </button>
          ))}
        </div>

        {/* Section Content */}
        <div className="min-h-[500px]">
          {activeSection === 'acts' && renderActReferences()}
          {activeSection === 'stamp-duty' && renderStampDutyCalculator()}
          {activeSection === 'gst' && renderGSTAnalysis()}
          {activeSection === 'registration' && renderRegistrationRequirements()}
        </div>
      </div>
    </div>
  );
};

export default IndianLegalAnalysis;