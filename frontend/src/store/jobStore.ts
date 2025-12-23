/**
 * =============================================================================
 * SMARTCAREER AI - Job Store
 * =============================================================================
 *
 * Zustand store for job listings state management.
 */

import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import { get as apiGet, post, put, del } from "@/lib/api";
import type {
  Job,
  JobSearchParams,
  JobCreateRequest,
  JobMatchResult,
  PaginatedResponse,
} from "@/types/api";

// =============================================================================
// TYPES
// =============================================================================

interface JobState {
  // State
  jobs: Job[];
  myJobs: Job[]; // Company's own jobs
  currentJob: Job | null;
  searchParams: JobSearchParams;
  totalJobs: number;
  totalPages: number;
  currentPage: number;
  isLoading: boolean;
  error: string | null;

  // Match results
  matchResults: JobMatchResult[];
  isMatching: boolean;

  // Actions
  searchJobs: (params?: JobSearchParams) => Promise<void>;
  fetchJob: (id: string) => Promise<Job>;
  fetchMyJobs: () => Promise<void>;
  createJob: (data: JobCreateRequest) => Promise<Job>;
  updateJob: (id: string, data: Partial<JobCreateRequest>) => Promise<Job>;
  deleteJob: (id: string) => Promise<void>;
  publishJob: (id: string) => Promise<void>;
  closeJob: (id: string) => Promise<void>;
  matchJobs: (resumeId: string) => Promise<JobMatchResult[]>;

  // Helpers
  setSearchParams: (params: Partial<JobSearchParams>) => void;
  setCurrentJob: (job: Job | null) => void;
  clearError: () => void;
  resetSearch: () => void;
}

// =============================================================================
// DEFAULT SEARCH PARAMS
// =============================================================================

const defaultSearchParams: JobSearchParams = {
  page: 1,
  page_size: 12,
  sort_by: "created_at",
  sort_order: "desc",
};

// =============================================================================
// STORE
// =============================================================================

export const useJobStore = create<JobState>()(
  immer((set, get) => ({
    // =======================================================================
    // INITIAL STATE
    // =======================================================================
    jobs: [],
    myJobs: [],
    currentJob: null,
    searchParams: defaultSearchParams,
    totalJobs: 0,
    totalPages: 0,
    currentPage: 1,
    isLoading: false,
    error: null,
    matchResults: [],
    isMatching: false,

    // =======================================================================
    // SEARCH JOBS
    // =======================================================================
    searchJobs: async (params?: JobSearchParams) => {
      const searchParams = params || get().searchParams;

      set((state) => {
        state.isLoading = true;
        state.error = null;
        state.searchParams = { ...state.searchParams, ...params };
      });

      try {
        const response = await apiGet<{
          jobs: Job[];
          total: number;
          page: number;
          page_size: number;
          total_pages: number;
        }>("/jobs", searchParams as Record<string, unknown>);

        set((state) => {
          state.jobs = response.jobs;
          state.totalJobs = response.total;
          state.totalPages = response.total_pages;
          state.currentPage = response.page;
          state.isLoading = false;
        });
      } catch (error: unknown) {
        const errorMessage = (error as { message?: string })?.message || "Failed to search jobs";
        set((state) => {
          state.error = errorMessage;
          state.isLoading = false;
        });
      }
    },

    // =======================================================================
    // FETCH SINGLE JOB
    // =======================================================================
    fetchJob: async (id: string) => {
      set((state) => {
        state.isLoading = true;
        state.error = null;
      });

      try {
        const job = await apiGet<Job>(`/jobs/${id}`);
        set((state) => {
          state.currentJob = job;
          state.isLoading = false;
        });
        return job;
      } catch (error: unknown) {
        const errorMessage = (error as { message?: string })?.message || "Failed to fetch job";
        set((state) => {
          state.error = errorMessage;
          state.isLoading = false;
        });
        throw error;
      }
    },

    // =======================================================================
    // FETCH MY JOBS (Company)
    // =======================================================================
    fetchMyJobs: async () => {
      set((state) => {
        state.isLoading = true;
        state.error = null;
      });

      try {
        const response = await apiGet<{ jobs: Job[] }>("/jobs/my");
        set((state) => {
          state.myJobs = response.jobs;
          state.isLoading = false;
        });
      } catch (error: unknown) {
        const errorMessage = (error as { message?: string })?.message || "Failed to fetch your jobs";
        set((state) => {
          state.error = errorMessage;
          state.isLoading = false;
        });
      }
    },

    // =======================================================================
    // CREATE JOB
    // =======================================================================
    createJob: async (data: JobCreateRequest) => {
      set((state) => {
        state.isLoading = true;
        state.error = null;
      });

      try {
        const job = await post<Job>("/jobs", data);
        set((state) => {
          state.myJobs.unshift(job);
          state.currentJob = job;
          state.isLoading = false;
        });
        return job;
      } catch (error: unknown) {
        const errorMessage = (error as { message?: string })?.message || "Failed to create job";
        set((state) => {
          state.error = errorMessage;
          state.isLoading = false;
        });
        throw error;
      }
    },

    // =======================================================================
    // UPDATE JOB
    // =======================================================================
    updateJob: async (id: string, data: Partial<JobCreateRequest>) => {
      set((state) => {
        state.isLoading = true;
        state.error = null;
      });

      try {
        const job = await put<Job>(`/jobs/${id}`, data);
        set((state) => {
          // Update in myJobs
          const myIndex = state.myJobs.findIndex((j) => j.id === id);
          if (myIndex !== -1) {
            state.myJobs[myIndex] = job;
          }
          // Update in jobs
          const index = state.jobs.findIndex((j) => j.id === id);
          if (index !== -1) {
            state.jobs[index] = job;
          }
          if (state.currentJob?.id === id) {
            state.currentJob = job;
          }
          state.isLoading = false;
        });
        return job;
      } catch (error: unknown) {
        const errorMessage = (error as { message?: string })?.message || "Failed to update job";
        set((state) => {
          state.error = errorMessage;
          state.isLoading = false;
        });
        throw error;
      }
    },

    // =======================================================================
    // DELETE JOB
    // =======================================================================
    deleteJob: async (id: string) => {
      set((state) => {
        state.isLoading = true;
        state.error = null;
      });

      try {
        await del(`/jobs/${id}`);
        set((state) => {
          state.myJobs = state.myJobs.filter((j) => j.id !== id);
          state.jobs = state.jobs.filter((j) => j.id !== id);
          if (state.currentJob?.id === id) {
            state.currentJob = null;
          }
          state.isLoading = false;
        });
      } catch (error: unknown) {
        const errorMessage = (error as { message?: string })?.message || "Failed to delete job";
        set((state) => {
          state.error = errorMessage;
          state.isLoading = false;
        });
        throw error;
      }
    },

    // =======================================================================
    // PUBLISH JOB
    // =======================================================================
    publishJob: async (id: string) => {
      try {
        const job = await post<Job>(`/jobs/${id}/publish`);
        set((state) => {
          const myIndex = state.myJobs.findIndex((j) => j.id === id);
          if (myIndex !== -1) {
            state.myJobs[myIndex] = job;
          }
          if (state.currentJob?.id === id) {
            state.currentJob = job;
          }
        });
      } catch (error: unknown) {
        const errorMessage = (error as { message?: string })?.message || "Failed to publish job";
        set((state) => {
          state.error = errorMessage;
        });
        throw error;
      }
    },

    // =======================================================================
    // CLOSE JOB
    // =======================================================================
    closeJob: async (id: string) => {
      try {
        const job = await post<Job>(`/jobs/${id}/close`);
        set((state) => {
          const myIndex = state.myJobs.findIndex((j) => j.id === id);
          if (myIndex !== -1) {
            state.myJobs[myIndex] = job;
          }
          if (state.currentJob?.id === id) {
            state.currentJob = job;
          }
        });
      } catch (error: unknown) {
        const errorMessage = (error as { message?: string })?.message || "Failed to close job";
        set((state) => {
          state.error = errorMessage;
        });
        throw error;
      }
    },

    // =======================================================================
    // MATCH JOBS (AI)
    // =======================================================================
    matchJobs: async (resumeId: string) => {
      set((state) => {
        state.isMatching = true;
        state.error = null;
      });

      try {
        const response = await post<{ matches: JobMatchResult[] }>("/jobs/match", {
          resume_id: resumeId,
        });
        set((state) => {
          state.matchResults = response.matches;
          state.isMatching = false;
        });
        return response.matches;
      } catch (error: unknown) {
        const errorMessage = (error as { message?: string })?.message || "Failed to match jobs";
        set((state) => {
          state.error = errorMessage;
          state.isMatching = false;
        });
        throw error;
      }
    },

    // =======================================================================
    // HELPERS
    // =======================================================================
    setSearchParams: (params: Partial<JobSearchParams>) => {
      set((state) => {
        state.searchParams = { ...state.searchParams, ...params };
      });
    },

    setCurrentJob: (job: Job | null) => {
      set((state) => {
        state.currentJob = job;
      });
    },

    clearError: () => {
      set((state) => {
        state.error = null;
      });
    },

    resetSearch: () => {
      set((state) => {
        state.searchParams = defaultSearchParams;
        state.jobs = [];
        state.totalJobs = 0;
        state.totalPages = 0;
        state.currentPage = 1;
      });
    },
  }))
);

// =============================================================================
// SELECTORS
// =============================================================================

export const selectJobs = (state: JobState) => state.jobs;
export const selectMyJobs = (state: JobState) => state.myJobs;
export const selectCurrentJob = (state: JobState) => state.currentJob;
export const selectIsLoading = (state: JobState) => state.isLoading;
export const selectError = (state: JobState) => state.error;
export const selectSearchParams = (state: JobState) => state.searchParams;
export const selectMatchResults = (state: JobState) => state.matchResults;
export const selectIsMatching = (state: JobState) => state.isMatching;
export const selectPagination = (state: JobState) => ({
  total: state.totalJobs,
  totalPages: state.totalPages,
  currentPage: state.currentPage,
});
















