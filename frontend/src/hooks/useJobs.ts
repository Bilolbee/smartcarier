/**
 * =============================================================================
 * useJobs Hook
 * =============================================================================
 *
 * Custom hook for job operations
 */

"use client";

import { useCallback, useState } from "react";
import type { Job } from "@/types/api";

// =============================================================================
// TYPES
// =============================================================================

interface JobsState {
  jobs: Job[];
  currentJob: Job | null;
  isLoading: boolean;
  error: string | null;
  totalCount: number;
  currentPage: number;
  totalPages: number;
}

interface JobFilters {
  search?: string;
  location?: string;
  job_type?: string[];
  experience_level?: string[];
  salary_min?: number;
  salary_max?: number;
  sort_by?: "created_at" | "salary" | "relevance";
}

// =============================================================================
// MOCK DATA
// =============================================================================

const mockJobs: Job[] = [
  {
    id: "job-1",
    company_id: "company-1",
    title: "Senior Backend Developer",
    description: "We are looking for an experienced backend developer to join our team.",
    requirements: {
      skills: ["Python", "FastAPI", "PostgreSQL"],
      experience: "3+ years",
    },
    salary_min: 3000,
    salary_max: 5000,
    location: "Tashkent",
    job_type: "full_time",
    experience_level: "senior",
    status: "active",
    applications_count: 12,
    views_count: 156,
    created_at: "2024-01-15T10:00:00Z",
    updated_at: "2024-01-15T10:00:00Z",
    company: {
      name: "EPAM Systems",
      logo_url: "/logos/epam.png",
    },
  },
  {
    id: "job-2",
    company_id: "company-2",
    title: "Full Stack Engineer",
    description: "Join our dynamic team as a full stack engineer.",
    requirements: {
      skills: ["React", "Node.js", "TypeScript"],
      experience: "2+ years",
    },
    salary_min: 2500,
    salary_max: 4000,
    location: "Remote",
    job_type: "remote",
    experience_level: "mid",
    status: "active",
    applications_count: 25,
    views_count: 234,
    created_at: "2024-01-14T10:00:00Z",
    updated_at: "2024-01-14T10:00:00Z",
    company: {
      name: "Uzum Market",
      logo_url: "/logos/uzum.png",
    },
  },
];

// =============================================================================
// HOOK
// =============================================================================

export function useJobs() {
  const [state, setState] = useState<JobsState>({
    jobs: mockJobs,
    currentJob: null,
    isLoading: false,
    error: null,
    totalCount: 2,
    currentPage: 1,
    totalPages: 1,
  });

  const [filters, setFilters] = useState<JobFilters>({});

  // Fetch jobs
  const fetchJobs = useCallback(async (newFilters?: JobFilters, page: number = 1) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      // Update filters if provided
      if (newFilters) {
        setFilters(newFilters);
      }

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      // In real app: const response = await api.get('/jobs', { params: { ...filters, page } });
      
      setState((prev) => ({
        ...prev,
        jobs: mockJobs,
        isLoading: false,
        totalCount: mockJobs.length,
        currentPage: page,
        totalPages: 1,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: "Failed to fetch jobs",
      }));
    }
  }, []);

  // Fetch single job
  const fetchJob = useCallback(async (id: string) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      // In real app: const response = await api.get(`/jobs/${id}`);
      const job = mockJobs.find((j) => j.id === id);
      
      setState((prev) => ({
        ...prev,
        currentJob: job || null,
        isLoading: false,
      }));

      return job;
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: "Failed to fetch job",
      }));
    }
  }, []);

  // Search jobs
  const searchJobs = useCallback(async (query: string) => {
    return fetchJobs({ ...filters, search: query });
  }, [fetchJobs, filters]);

  // Apply filters
  const applyFilters = useCallback(async (newFilters: JobFilters) => {
    return fetchJobs({ ...filters, ...newFilters });
  }, [fetchJobs, filters]);

  // Clear filters
  const clearFilters = useCallback(async () => {
    setFilters({});
    return fetchJobs({});
  }, [fetchJobs]);

  // Match jobs to resume (AI)
  const matchJobs = useCallback(async (resumeId: string) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      // Simulate AI matching
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // In real app: const response = await api.post('/jobs/match', { resume_id: resumeId });
      
      // Return mock matched jobs with scores
      const matchedJobs = mockJobs.map((job, index) => ({
        ...job,
        matchScore: 95 - index * 7,
      }));

      setState((prev) => ({
        ...prev,
        jobs: matchedJobs,
        isLoading: false,
      }));

      return matchedJobs;
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: "Failed to match jobs",
      }));
      throw error;
    }
  }, []);

  // Save job
  const saveJob = useCallback(async (jobId: string) => {
    try {
      // In real app: await api.post(`/jobs/${jobId}/save`);
      console.log("Job saved:", jobId);
    } catch (error) {
      throw error;
    }
  }, []);

  // Unsave job
  const unsaveJob = useCallback(async (jobId: string) => {
    try {
      // In real app: await api.delete(`/jobs/${jobId}/save`);
      console.log("Job unsaved:", jobId);
    } catch (error) {
      throw error;
    }
  }, []);

  return {
    ...state,
    filters,
    fetchJobs,
    fetchJob,
    searchJobs,
    applyFilters,
    clearFilters,
    matchJobs,
    saveJob,
    unsaveJob,
  };
}

export default useJobs;
