/**
 * =============================================================================
 * useResume Hook
 * =============================================================================
 *
 * Custom hook for resume operations
 */

"use client";

import { useCallback, useState } from "react";
import type { Resume } from "@/types/api";

// =============================================================================
// TYPES
// =============================================================================

interface ResumeState {
  resumes: Resume[];
  currentResume: Resume | null;
  isLoading: boolean;
  isGenerating: boolean;
  error: string | null;
}

interface CreateResumeData {
  title: string;
  content: Record<string, any>;
}

interface GenerateResumeData {
  user_data: {
    name: string;
    email: string;
    phone?: string;
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
// HOOK
// =============================================================================

export function useResume() {
  const [state, setState] = useState<ResumeState>({
    resumes: [],
    currentResume: null,
    isLoading: false,
    isGenerating: false,
    error: null,
  });

  // Fetch all resumes
  const fetchResumes = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      // In real app: const response = await api.get('/resumes');
      
      setState((prev) => ({
        ...prev,
        resumes: [],
        isLoading: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: "Failed to fetch resumes",
      }));
    }
  }, []);

  // Fetch single resume
  const fetchResume = useCallback(async (id: string) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      // In real app: const response = await api.get(`/resumes/${id}`);
      
      setState((prev) => ({
        ...prev,
        currentResume: null,
        isLoading: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: "Failed to fetch resume",
      }));
    }
  }, []);

  // Create resume manually
  const createResume = useCallback(async (data: CreateResumeData) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      // In real app: const response = await api.post('/resumes', data);
      
      const newResume: Resume = {
        id: `resume-${Date.now()}`,
        user_id: "user-1",
        title: data.title,
        content: data.content,
        ai_generated: false,
        status: "draft",
        view_count: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      setState((prev) => ({
        ...prev,
        resumes: [newResume, ...prev.resumes],
        currentResume: newResume,
        isLoading: false,
      }));

      return newResume;
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: "Failed to create resume",
      }));
      throw error;
    }
  }, []);

  // Generate resume with AI
  const generateResume = useCallback(async (data: GenerateResumeData) => {
    setState((prev) => ({ ...prev, isGenerating: true, error: null }));

    try {
      // Simulate AI generation (takes longer)
      await new Promise((resolve) => setTimeout(resolve, 3000));

      // In real app: const response = await api.post('/resumes/generate-ai', data);
      
      const newResume: Resume = {
        id: `resume-${Date.now()}`,
        user_id: "user-1",
        title: `${data.user_data.name} - ${data.template || "Modern"} Resume`,
        content: {
          personal_info: {
            name: data.user_data.name,
            email: data.user_data.email,
            phone: data.user_data.phone,
          },
          summary: "AI-generated professional summary...",
          experience: data.user_data.experience,
          education: data.user_data.education,
          skills: data.user_data.skills,
        },
        ai_generated: true,
        status: "draft",
        view_count: 0,
        ats_score: 92,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      setState((prev) => ({
        ...prev,
        resumes: [newResume, ...prev.resumes],
        currentResume: newResume,
        isGenerating: false,
      }));

      return newResume;
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isGenerating: false,
        error: "Failed to generate resume",
      }));
      throw error;
    }
  }, []);

  // Update resume
  const updateResume = useCallback(async (id: string, data: Partial<Resume>) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      // In real app: const response = await api.put(`/resumes/${id}`, data);
      
      setState((prev) => ({
        ...prev,
        resumes: prev.resumes.map((r) =>
          r.id === id ? { ...r, ...data, updated_at: new Date().toISOString() } : r
        ),
        currentResume:
          prev.currentResume?.id === id
            ? { ...prev.currentResume, ...data, updated_at: new Date().toISOString() }
            : prev.currentResume,
        isLoading: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: "Failed to update resume",
      }));
      throw error;
    }
  }, []);

  // Delete resume
  const deleteResume = useCallback(async (id: string) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      // In real app: await api.delete(`/resumes/${id}`);
      
      setState((prev) => ({
        ...prev,
        resumes: prev.resumes.filter((r) => r.id !== id),
        currentResume: prev.currentResume?.id === id ? null : prev.currentResume,
        isLoading: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: "Failed to delete resume",
      }));
      throw error;
    }
  }, []);

  // Publish resume
  const publishResume = useCallback(async (id: string) => {
    return updateResume(id, { status: "published" });
  }, [updateResume]);

  // Archive resume
  const archiveResume = useCallback(async (id: string) => {
    return updateResume(id, { status: "archived" });
  }, [updateResume]);

  // Download resume as PDF
  const downloadResume = useCallback(async (id: string) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // In real app: Download the PDF
      // const blob = await api.get(`/resumes/${id}/download`, { responseType: 'blob' });
      // const url = window.URL.createObjectURL(blob);
      // const a = document.createElement('a');
      // a.href = url;
      // a.download = 'resume.pdf';
      // a.click();

      setState((prev) => ({
        ...prev,
        isLoading: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: "Failed to download resume",
      }));
      throw error;
    }
  }, []);

  return {
    ...state,
    fetchResumes,
    fetchResume,
    createResume,
    generateResume,
    updateResume,
    deleteResume,
    publishResume,
    archiveResume,
    downloadResume,
  };
}

export default useResume;
