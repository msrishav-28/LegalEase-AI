// User types
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user' | 'viewer';
  organization?: string;
  createdAt: string;
  lastLoginAt?: string;
}

// Document types
export interface Document {
  id: string;
  name: string;
  type: DocumentType;
  content?: string;
  metadata: DocumentMetadata;
  uploadedBy: string;
  uploadedAt: string;
  analysisStatus: AnalysisStatus;
  analysisResults?: AnalysisResults;
}

export type DocumentType = 'contract' | 'agreement' | 'mou' | 'nda' | 'invoice' | 'other';

export type AnalysisStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface DocumentMetadata {
  fileSize: number;
  pageCount: number;
  parties: string[];
  jurisdiction?: Jurisdiction;
  documentDate?: string;
  extractionMethod: 'text' | 'ocr';
}

// Jurisdiction types
export type Jurisdiction = 'india' | 'usa' | 'cross_border' | 'unknown';

export interface JurisdictionDetection {
  jurisdiction: Jurisdiction;
  confidence: number;
  scores: {
    india: number;
    usa: number;
  };
  usState?: string;
  detectedElements: string[];
}

// Analysis types
export interface AnalysisResults {
  id: string;
  documentId: string;
  summary: ExecutiveSummary;
  risks: Risk[];
  obligations: Obligation[];
  complexity: ComplexityScore;
  keyTerms: KeyTerm[];
  jurisdictionAnalysis?: JurisdictionAnalysis;
  createdAt: string;
}

export interface ExecutiveSummary {
  overview: string;
  keyPoints: string[];
  recommendations: string[];
}

export interface Risk {
  id: string;
  type: 'high' | 'medium' | 'low';
  category: string;
  description: string;
  impact: string;
  mitigation?: string;
  section?: string;
}

export interface Obligation {
  id: string;
  party: string;
  description: string;
  dueDate?: string;
  status: 'pending' | 'completed' | 'overdue';
  section?: string;
}

export interface ComplexityScore {
  overall: number;
  legal: number;
  financial: number;
  operational: number;
  explanation: string;
}

export interface KeyTerm {
  term: string;
  definition: string;
  importance: 'high' | 'medium' | 'low';
  section?: string;
}

export interface JurisdictionAnalysis {
  primary: Jurisdiction;
  confidence: number;
  indianAnalysis?: IndianLegalAnalysis;
  usAnalysis?: USLegalAnalysis;
  crossBorderAnalysis?: CrossBorderAnalysis;
}

export interface IndianLegalAnalysis {
  actReferences: ActReference[];
  stampDuty: StampDutyAnalysis;
  gstImplications: GSTAnalysis;
  registrationRequirements: RegistrationRequirement[];
}

export interface USLegalAnalysis {
  federalReferences: FederalLawReference[];
  stateJurisdiction: string;
  uccAnalysis: UCCAnalysis;
  securitiesCompliance: SecuritiesAnalysis;
  privacyCompliance?: PrivacyAnalysis;
  choiceOfLawAnalysis?: ChoiceOfLawAnalysis;
  arbitrationAnalysis?: ArbitrationAnalysis;
}

export interface CrossBorderAnalysis {
  enforceabilityComparison: EnforceabilityComparison;
  taxImplications: TaxImplications;
  recommendedGoverningLaw: string;
}

// Supporting interfaces
export interface ActReference {
  act: string;
  section: string;
  relevance: string;
}

export interface StampDutyAnalysis {
  state: string;
  amount: number;
  calculation: string;
  exemptions?: string[];
}

export interface GSTAnalysis {
  applicable: boolean;
  rate?: number;
  implications: string[];
}

export interface RegistrationRequirement {
  type: string;
  required: boolean;
  authority: string;
  timeline?: string;
}

export interface FederalLawReference {
  law: string;
  section: string;
  relevance: string;
}

export interface UCCAnalysis {
  applicable: boolean;
  articles: string[];
  implications: string[];
}

export interface SecuritiesAnalysis {
  applicable: boolean;
  regulations: string[];
  compliance: string[];
}

export interface PrivacyAnalysis {
  ccpaApplicable: boolean;
  gdprApplicable: boolean;
  requirements: string[];
  complianceChecklist: ComplianceChecklistItem[];
}

export interface ChoiceOfLawAnalysis {
  currentGoverningLaw?: string;
  recommendedGoverningLaw: string;
  enforceabilityFactors: string[];
  conflictOfLawsIssues: string[];
  recommendations: string[];
}

export interface ArbitrationAnalysis {
  hasArbitrationClause: boolean;
  arbitrationRules?: string;
  seat?: string;
  enforceabilityAssessment: string;
  recommendations: string[];
  alternativeDispute: string[];
}

export interface ComplianceChecklistItem {
  item: string;
  completed: boolean;
  required: boolean;
}

export interface EnforceabilityComparison {
  india: EnforceabilityFactors;
  usa: EnforceabilityFactors;
  recommendations: string[];
}

export interface EnforceabilityFactors {
  formalities: string[];
  requirements: string[];
  challenges: string[];
}

export interface TaxImplications {
  indiaImplications: string[];
  usImplications: string[];
  dtaaConsiderations: string[];
  comparisonSummary: string;
  recommendedStructure?: string;
}

export interface FormalitiesComparison {
  india: {
    stampDuty: {
      required: boolean;
      amount: string;
      exemptions: string[];
    };
    registration: {
      required: boolean;
      authority: string;
      timeline: string;
    };
    witnesses: {
      required: boolean;
      count: number;
      requirements: string[];
    };
    notarization: {
      required: boolean;
      type: string;
    };
  };
  usa: {
    notarization: {
      required: boolean;
      type: string;
      stateRequirements: string[];
    };
    witnesses: {
      required: boolean;
      count: number;
      requirements: string[];
    };
    recording: {
      required: boolean;
      authority: string;
      fees: string;
    };
    acknowledgment: {
      required: boolean;
      type: string;
    };
  };
  differences: string[];
  recommendations: string[];
}

export interface ComplianceGap {
  jurisdiction: 'india' | 'usa';
  requirement: string;
  status: 'missing' | 'partial' | 'conflicting';
  impact: 'high' | 'medium' | 'low';
  recommendation: string;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// Search types
export interface SearchResult {
  id: string;
  documentId: string;
  content: string;
  score: number;
  metadata: Record<string, any>;
  highlights?: string[];
}

export interface SearchFilters {
  documentType?: DocumentType[];
  jurisdiction?: Jurisdiction[];
  dateRange?: {
    start: string;
    end: string;
  };
  analysisStatus?: AnalysisStatus[];
}

// WebSocket types
export interface WebSocketMessage {
  type: string;
  payload: any;
  timestamp: string;
}

export interface TaskProgress {
  taskId: string;
  progress: number;
  total: number;
  message: string;
  status: 'running' | 'completed' | 'failed';
}

// Document Comparison types
export interface DocumentComparison {
  id: string;
  document1: Document;
  document2: Document;
  differences: DocumentDifference[];
  similarities: ClauseSimilarity[];
  comparisonMetrics: ComparisonMetrics;
  createdAt: string;
}

export interface DocumentDifference {
  id: string;
  type: 'added' | 'removed' | 'modified';
  section: string;
  document1Content?: string;
  document2Content?: string;
  document1Position?: TextPosition;
  document2Position?: TextPosition;
  severity: 'high' | 'medium' | 'low';
  category: 'clause' | 'term' | 'obligation' | 'party' | 'date' | 'amount' | 'other';
  description: string;
}

export interface ClauseSimilarity {
  id: string;
  document1Clause: DocumentClause;
  document2Clause: DocumentClause;
  similarityScore: number;
  type: 'identical' | 'similar' | 'related';
  differences?: string[];
}

export interface DocumentClause {
  id: string;
  content: string;
  section: string;
  position: TextPosition;
  type: string;
  importance: 'high' | 'medium' | 'low';
}

export interface TextPosition {
  pageNumber: number;
  startOffset: number;
  endOffset: number;
  boundingBox?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

export interface ComparisonMetrics {
  overallSimilarity: number;
  structuralSimilarity: number;
  contentSimilarity: number;
  legalSimilarity: number;
  totalDifferences: number;
  criticalDifferences: number;
  addedClauses: number;
  removedClauses: number;
  modifiedClauses: number;
}

export interface ComparisonExport {
  format: 'pdf' | 'docx' | 'html' | 'json';
  includeHighlights: boolean;
  includeSummary: boolean;
  includeMetrics: boolean;
  sections?: string[];
}

// Chat types
export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  documentId?: string;
  jurisdiction?: Jurisdiction;
  jurisdictionBadge?: JurisdictionBadge;
  references?: DocumentReference[];
  confidence?: number;
  status?: 'sending' | 'sent' | 'error';
  metadata?: ChatMessageMetadata;
}

export interface JurisdictionBadge {
  jurisdiction: Jurisdiction;
  confidence: number;
  color: 'blue' | 'green' | 'orange' | 'purple';
  label: string;
}

export interface DocumentReference {
  documentId: string;
  documentName: string;
  section?: string;
  pageNumber?: number;
  relevance: number;
  excerpt: string;
  jurisdiction?: Jurisdiction;
}

export interface ChatMessageMetadata {
  processingTime?: number;
  modelUsed?: string;
  tokensUsed?: number;
  jurisdictionContext?: JurisdictionContext;
}

export interface JurisdictionContext {
  detectedJurisdiction: Jurisdiction;
  confidence: number;
  applicableLaws: string[];
  relevantCases?: string[];
  complianceRequirements?: string[];
}

export interface ChatSession {
  id: string;
  documentId?: string;
  messages: ChatMessage[];
  jurisdiction?: Jurisdiction;
  createdAt: string;
  updatedAt: string;
  title?: string;
  isActive: boolean;
}

export interface ChatAutoComplete {
  suggestions: ChatSuggestion[];
  jurisdiction?: Jurisdiction;
}

export interface ChatSuggestion {
  text: string;
  type: 'question' | 'command' | 'legal_term' | 'jurisdiction_specific';
  jurisdiction?: Jurisdiction;
  description?: string;
  category: string;
}

export interface TypingIndicator {
  userId: string;
  userName: string;
  isTyping: boolean;
  jurisdiction?: Jurisdiction;
}

// Form types
export interface LoginForm {
  email: string;
  password: string;
}

export interface RegisterForm {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
  organization?: string;
}

export interface UploadForm {
  files: File[];
  documentType: DocumentType;
  jurisdiction?: Jurisdiction;
  description?: string;
}