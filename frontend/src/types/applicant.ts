// Applicant Types based on API Response Schema

export type PersonStatus = 'active' | 'onboarding' | 'offboarding' | 'archived';

export interface Document {
  id: string;
  file_name: string;
  file_type: string;
  file_path: string;
  uploaded_at: string;
}

export interface ExtractedSkills {
  technical: string[];
  soft: string[];
  languages: string[];
}

export interface ExtractedExperience {
  company: string;
  role: string;
  duration: string;
  description: string;
}

export interface ExtractedEducation {
  institution: string;
  degree: string;
  field: string;
  year: string;
}

export interface ExtractedData {
  skills?: ExtractedSkills;
  experience?: ExtractedExperience[];
  education?: ExtractedEducation[];
  summary?: string;
}

export interface Applicant {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  status: PersonStatus;
  matching_score: number | null;
  extracted_data: ExtractedData | null;
  created_at: string;
  documents: Document[];
}

// API Request Types
export interface CreateApplicantRequest {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
}

export interface ApplicantFilters {
  status?: PersonStatus | 'all';
  min_score?: number;
  max_score?: number;
  date_from?: string;
  date_to?: string;
  page?: number;
  page_size?: number;
  search?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface UpdateStatusRequest {
  status: PersonStatus;
}

export interface InviteRequest {
  template_id?: string;
  custom_message?: string;
}

// Upload CV Types
export interface CVUploadResponse {
  id: string;
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  message: string;
}

// UI State Types
export type ScoreRange = {
  min: number;
  max: number;
};

export interface FilterState {
  status: PersonStatus | 'all';
  scoreRange: ScoreRange;
  dateFrom: string | null;
  dateTo: string | null;
  search: string;
}

export type StatusFilter = PersonStatus | 'all';
