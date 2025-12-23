/**
 * =============================================================================
 * API TYPES
 * =============================================================================
 *
 * TypeScript interfaces for API request/response bodies
 */

// =============================================================================
// USER TYPES
// =============================================================================

export type UserRole = "student" | "company" | "admin";

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  avatar_url?: string;
  company_name?: string;
  created_at: string;
  updated_at?: string;
  last_login?: string;
}

export interface UserProfile extends User {
  resumes_count?: number;
  applications_count?: number;
  jobs_posted?: number;
}

// =============================================================================
// AUTH TYPES
// =============================================================================

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  phone?: string;
  role?: UserRole;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthResponse {
  success: boolean;
  data: {
    user: User;
    tokens: TokenResponse;
  };
  message?: string;
}

// =============================================================================
// RESUME TYPES
// =============================================================================

export type ResumeStatus = "draft" | "published" | "archived";

export interface ResumeContent {
  personal_info?: {
    name?: string;
    email?: string;
    phone?: string;
    location?: string;
    linkedin_url?: string;
    portfolio_url?: string;
    professional_title?: string;
  };
  summary?: string;
  experience?: Array<{
    company: string;
    position: string;
    start_date: string;
    end_date?: string;
    is_current?: boolean;
    description: string;
    achievements?: string[];
  }>;
  education?: Array<{
    institution: string;
    degree: string;
    field?: string;
    year: string;
    gpa?: string;
  }>;
  skills?: {
    technical?: string[];
    soft?: string[];
  };
  languages?: Array<{
    name: string;
    proficiency: string;
  }>;
  certifications?: Array<{
    name: string;
    issuer: string;
    year: string;
  }>;
  projects?: Array<{
    name: string;
    description: string;
    url?: string;
    technologies?: string[];
  }>;
}

export interface Resume {
  id: string;
  user_id: string;
  title: string;
  content: ResumeContent;
  ai_generated: boolean;
  pdf_url?: string;
  status: ResumeStatus;
  view_count: number;
  ats_score?: number;
  created_at: string;
  updated_at: string;
}

export interface ResumeCreateRequest {
  title: string;
  content: ResumeContent;
}

export interface ResumeGenerateRequest {
  user_data: {
    name: string;
    email: string;
    phone?: string;
    location?: string;
    professional_title?: string;
    skills: string[];
    experience: Array<{
      company: string;
      position: string;
      duration: string;
      description: string;
    }>;
    education: Array<{
      institution: string;
      degree: string;
      field?: string;
      year: string;
    }>;
  };
  template?: "modern" | "classic" | "minimal" | "creative";
  tone?: "professional" | "confident" | "friendly" | "technical";
}

// =============================================================================
// JOB TYPES
// =============================================================================

export type JobType = "full_time" | "part_time" | "remote" | "hybrid" | "contract";
export type ExperienceLevel = "junior" | "mid" | "senior" | "lead" | "executive";
export type JobStatus = "draft" | "active" | "closed";

export interface JobRequirements {
  skills?: string[];
  experience?: string;
  education?: string;
  certifications?: string[];
}

export interface Job {
  id: string;
  company_id: string;
  title: string;
  description: string;
  requirements: JobRequirements;
  salary_min?: number;
  salary_max?: number;
  location: string;
  job_type: JobType;
  experience_level: ExperienceLevel;
  status: JobStatus;
  applications_count: number;
  views_count: number;
  created_at: string;
  updated_at: string;
  expires_at?: string;
  company?: {
    name: string;
    logo_url?: string;
  };
  matchScore?: number;
}

export interface JobCreateRequest {
  title: string;
  description: string;
  requirements: JobRequirements;
  salary_min?: number;
  salary_max?: number;
  location: string;
  job_type: JobType;
  experience_level: ExperienceLevel;
  expires_at?: string;
}

export interface JobSearchParams {
  search?: string;
  location?: string;
  job_type?: JobType[];
  experience_level?: ExperienceLevel[];
  salary_min?: number;
  salary_max?: number;
  sort_by?: "created_at" | "salary" | "relevance";
  page?: number;
  limit?: number;
}

// =============================================================================
// APPLICATION TYPES
// =============================================================================

export type ApplicationStatus = "pending" | "reviewing" | "interview" | "rejected" | "accepted";

export interface Application {
  id: string;
  job_id: string;
  user_id: string;
  resume_id: string;
  cover_letter?: string;
  status: ApplicationStatus;
  applied_at: string;
  reviewed_at?: string;
  interview_at?: string;
  updated_at: string;
  job?: Job;
  resume?: Resume;
  applicant?: User;
}

export interface ApplicationCreateRequest {
  job_id: string;
  resume_id: string;
  cover_letter?: string;
}

export interface AutoApplyRequest {
  criteria: {
    job_types?: JobType[];
    locations?: string[];
    experience_levels?: ExperienceLevel[];
    salary_min?: number;
    max_applications?: number;
  };
  resume_id: string;
}

// =============================================================================
// API RESPONSE TYPES
// =============================================================================

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  meta?: {
    timestamp: string;
    request_id: string;
  };
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: {
    items: T[];
    total: number;
    page: number;
    limit: number;
    pages: number;
  };
  message?: string;
}

export interface ApiError {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Record<string, string[]>;
  };
}
