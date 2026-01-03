/**
 * Type definitions for the AI Job Assistant browser extension
 */

// Personal Information
export interface PersonalInfo {
  fullName: string;
  firstName?: string;
  lastName?: string;
  middleName?: string;
  email: string;
  phone: string;
  location?: string; // City, State or full address
  address?: {
    street?: string;
    city?: string;
    state?: string;
    zipCode?: string;
    country?: string;
  };
  linkedinUrl?: string;
  githubUrl?: string;
  portfolioUrl?: string;
}

// Work Experience
export interface WorkExperience {
  id: string;
  companyName: string;
  jobTitle: string;
  startDate: string; // ISO format YYYY-MM-DD
  endDate?: string; // ISO format or null if current
  isCurrent: boolean;
  location?: string;
  description?: string;
  achievements?: string[];
}

// Education
export interface Education {
  id: string;
  institution: string;
  degree?: string; // e.g., "Bachelor of Science"
  degreeType?: string; // e.g., "Bachelor's", "Master's"
  fieldOfStudy?: string;
  startDate?: string;
  endDate?: string;
  gpa?: number;
  location?: string;
}

// Skills
export interface Skill {
  id: string;
  name: string;
  category?: string;
  proficiencyLevel?: string;
}

// Demographic Answers (optional, user-configurable)
export interface DemographicAnswers {
  race?: string;
  gender?: string;
  veteranStatus?: string;
  disabilityStatus?: string;
  [key: string]: string | undefined; // Allow custom fields
}

// Application Data - Complete data structure for autofill
export interface ApplicationData {
  personalInfo: PersonalInfo;
  workExperience: WorkExperience[]; // Singular for consistency with strategies
  workExperiences?: WorkExperience[]; // Plural for backwards compatibility
  education: Education[];
  skills?: Skill[];
  resumeFile?: File;
  coverLetter?: string; // Cover letter text content
  coverLetterFile?: File;
  demographics?: DemographicAnswers;
}

// Autofill Result
export interface AutofillResult {
  success: boolean;
  platform?: string; // ATS platform name
  fieldsFilledCount?: number; // Number of fields filled
  fieldsCompleted?: number; // Backwards compatibility
  totalFields?: number;
  fieldsFailed?: string[];
  message?: string; // Error or success message
  errors?: string[];
  duration?: number; // milliseconds
}

// Autofill Progress (for real-time updates)
export interface AutofillProgress {
  currentStep: string;
  percentage: number;
  fieldsCompleted: number;
  totalFields: number;
}

// Submit Result
export interface SubmitResult {
  success: boolean;
  message: string;
  error?: string;
}

// ATS Platform Type
export type ATSPlatform = 'workday' | 'greenhouse' | 'lever' | 'taleo' | 'unknown';

// ATS Strategy Interface
export interface ATSStrategy {
  detect(): boolean;
  autofill(data: ApplicationData): Promise<AutofillResult>;
  getPlatformName(): string;
  submit?(): Promise<SubmitResult>;
}

// Extension Settings
export interface ExtensionSettings {
  apiBaseUrl: string;
  authToken?: string;
  enabledPlatforms: {
    workday: boolean;
    greenhouse: boolean;
    lever: boolean;
    taleo: boolean;
  };
  autoSubmit: boolean; // Default: false (opt-in only)
  defaultResumeVersionId?: string;
  demographics?: DemographicAnswers;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ResumeData {
  id: string;
  personalInfo: PersonalInfo;
  workExperiences: WorkExperience[];
  education: Education[];
  skills: Skill[];
  resumeFileUrl?: string;
}

export interface ApplicationTemplate {
  jobId: string;
  resumeVersionId: string;
  coverLetterId?: string;
  resumeFileUrl: string;
  coverLetterFileUrl?: string;
}

// Activity Log Entry
export interface ActivityLogEntry {
  timestamp: number;
  platform: ATSPlatform;
  url: string;
  action: 'autofill' | 'submit' | 'error';
  result: 'success' | 'partial' | 'failure';
  fieldsCompleted?: number;
  totalFields?: number;
  error?: string;
}

// Message Types for communication between components
export type MessageType = 
  | 'autofill-start'
  | 'autofill-data'
  | 'autofill-progress'
  | 'autofill-complete'
  | 'submit-start'
  | 'submit-complete'
  | 'get-settings'
  | 'update-settings'
  | 'detect-platform'
  | 'log-activity';

export interface ExtensionMessage<T = any> {
  type: MessageType;
  payload?: T;
}

// Storage Keys
export const StorageKeys = {
  SETTINGS: 'ai_job_assistant_settings',
  AUTH_TOKEN: 'ai_job_assistant_auth_token',
  ACTIVITY_LOG: 'ai_job_assistant_activity_log',
  LAST_SYNC: 'ai_job_assistant_last_sync',
} as const;
