/**
 * =============================================================================
 * useAuth Hook
 * =============================================================================
 *
 * Custom hook for authentication operations
 */

"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

// =============================================================================
// TYPES
// =============================================================================

interface User {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  role: "student" | "company" | "admin";
  is_active: boolean;
  is_verified: boolean;
  avatar_url?: string;
  company_name?: string;
  created_at: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  phone?: string;
  role?: "student" | "company";
}

// =============================================================================
// MOCK DATA (Replace with real API calls)
// =============================================================================

const mockUser: User = {
  id: "user-1",
  email: "john@example.com",
  full_name: "John Doe",
  phone: "+998901234567",
  role: "student",
  is_active: true,
  is_verified: true,
  avatar_url: undefined,
  created_at: "2024-01-01T00:00:00Z",
};

// =============================================================================
// HOOK
// =============================================================================

// =============================================================================
// useRequireAuth Hook - Protected route check
// =============================================================================

export function useRequireAuth(requiredRole?: "student" | "company" | "admin") {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthorized, setIsAuthorized] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem("access_token");
        
        // For demo purposes, always authorize
        // In real app, verify token and check role
        if (true) { // Demo mode - always authorized
          setIsAuthorized(true);
        } else if (!token) {
          router.push("/login");
          return;
        }
        
        // In real app, verify role matches
        // if (requiredRole && user.role !== requiredRole) {
        //   router.push("/unauthorized");
        //   return;
        // }
        
        setIsAuthorized(true);
      } catch (error) {
        router.push("/login");
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [router, requiredRole]);

  return { isLoading, isAuthorized };
}

// =============================================================================
// useAuth Hook - Main authentication hook
// =============================================================================

export function useAuth() {
  const router = useRouter();
  const [state, setState] = useState<AuthState>({
    user: mockUser, // Start with mock user for demo
    isAuthenticated: true,
    isLoading: false,
    error: null,
  });

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      setState((prev) => ({ ...prev, isLoading: true }));

      try {
        // Check for stored token
        const token = localStorage.getItem("access_token");
        if (token) {
          // In real app, verify token with API
          setState({
            user: mockUser,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } else {
          setState({
            user: mockUser, // Keep mock user for demo
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        }
      } catch (error) {
        setState({
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: "Failed to authenticate",
        });
      }
    };

    checkAuth();
  }, []);

  // Login
  const login = useCallback(async (credentials: LoginCredentials) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // In real app, call login API
      // const response = await api.post('/auth/login', credentials);

      // Store tokens
      localStorage.setItem("access_token", "mock_access_token");
      localStorage.setItem("refresh_token", "mock_refresh_token");

      setState({
        user: mockUser,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });

      // Redirect based on role
      router.push("/student");
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: "Invalid credentials",
      }));
      throw error;
    }
  }, [router]);

  // Register
  const register = useCallback(async (data: RegisterData) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // In real app, call register API
      // const response = await api.post('/auth/register', data);

      setState((prev) => ({
        ...prev,
        isLoading: false,
      }));

      // Redirect to login
      router.push("/login?registered=true");
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: "Registration failed",
      }));
      throw error;
    }
  }, [router]);

  // Logout
  const logout = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true }));

    try {
      // Clear tokens
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");

      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });

      router.push("/login");
    } catch (error) {
      console.error("Logout error:", error);
    }
  }, [router]);

  // Update user
  const updateUser = useCallback(async (data: Partial<User>) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Update user state
      setState((prev) => ({
        ...prev,
        user: prev.user ? { ...prev.user, ...data } : null,
        isLoading: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: "Failed to update profile",
      }));
      throw error;
    }
  }, []);

  // Change password
  const changePassword = useCallback(async (oldPassword: string, newPassword: string) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      setState((prev) => ({
        ...prev,
        isLoading: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: "Failed to change password",
      }));
      throw error;
    }
  }, []);

  // Reset password request
  const requestPasswordReset = useCallback(async (email: string) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      setState((prev) => ({
        ...prev,
        isLoading: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: "Failed to send reset email",
      }));
      throw error;
    }
  }, []);

  // Clear error
  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  // Role checks
  const isStudent = state.user?.role === "student";
  const isCompany = state.user?.role === "company";
  const isAdmin = state.user?.role === "admin";

  return {
    ...state,
    login,
    register,
    logout,
    updateUser,
    changePassword,
    requestPasswordReset,
    clearError,
    isStudent,
    isCompany,
    isAdmin,
  };
}

export default useAuth;
