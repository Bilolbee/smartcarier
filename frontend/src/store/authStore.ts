/**
 * =============================================================================
 * AUTH STORE - Zustand State Management
 * =============================================================================
 *
 * Handles authentication state:
 * - User data
 * - Tokens (access + refresh)
 * - Login/Logout actions
 * - Auth status
 */

import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { immer } from "zustand/middleware/immer";
import type { User } from "@/types/api";

// =============================================================================
// TYPES
// =============================================================================

interface AuthState {
  // State
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setUser: (user: User | null) => void;
  setTokens: (accessToken: string, refreshToken: string) => void;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<string | null>;
  updateProfile: (data: Partial<User>) => Promise<void>;
  clearError: () => void;
}

interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  phone?: string;
  role?: "student" | "company";
}

// =============================================================================
// STORE
// =============================================================================

export const useAuthStore = create<AuthState>()(
  persist(
    immer((set, get) => ({
      // Initial state
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Set user
      setUser: (user) =>
        set((state) => {
          state.user = user;
          state.isAuthenticated = !!user;
        }),

      // Set tokens
      setTokens: (accessToken, refreshToken) =>
        set((state) => {
          state.accessToken = accessToken;
          state.refreshToken = refreshToken;
          state.isAuthenticated = true;
        }),

      // Login
      login: async (email, password) => {
        set((state) => {
          state.isLoading = true;
          state.error = null;
        });

        try {
          // Simulate API call
          await new Promise((resolve) => setTimeout(resolve, 1000));

          // Mock response
          const mockUser: User = {
            id: "user-1",
            email,
            full_name: "John Doe",
            phone: "+998901234567",
            role: "student",
            is_active: true,
            is_verified: true,
            created_at: new Date().toISOString(),
          };

          set((state) => {
            state.user = mockUser;
            state.accessToken = "mock_access_token_" + Date.now();
            state.refreshToken = "mock_refresh_token_" + Date.now();
            state.isAuthenticated = true;
            state.isLoading = false;
          });
        } catch (error: any) {
          set((state) => {
            state.isLoading = false;
            state.error = error.message || "Login failed";
          });
          throw error;
        }
      },

      // Register
      register: async (data) => {
        set((state) => {
          state.isLoading = true;
          state.error = null;
        });

        try {
          // Simulate API call
          await new Promise((resolve) => setTimeout(resolve, 1000));

          // In real app, would call API
          set((state) => {
            state.isLoading = false;
          });
        } catch (error: any) {
          set((state) => {
            state.isLoading = false;
            state.error = error.message || "Registration failed";
          });
          throw error;
        }
      },

      // Logout
      logout: () =>
        set((state) => {
          state.user = null;
          state.accessToken = null;
          state.refreshToken = null;
          state.isAuthenticated = false;
          state.error = null;
        }),

      // Refresh access token
      refreshAccessToken: async () => {
        const { refreshToken } = get();
        if (!refreshToken) return null;

        try {
          // Simulate API call
          await new Promise((resolve) => setTimeout(resolve, 500));

          const newAccessToken = "mock_access_token_refreshed_" + Date.now();
          
          set((state) => {
            state.accessToken = newAccessToken;
          });

          return newAccessToken;
        } catch (error) {
          // If refresh fails, logout
          get().logout();
          return null;
        }
      },

      // Update profile
      updateProfile: async (data) => {
        set((state) => {
          state.isLoading = true;
          state.error = null;
        });

        try {
          // Simulate API call
          await new Promise((resolve) => setTimeout(resolve, 500));

          set((state) => {
            if (state.user) {
              state.user = { ...state.user, ...data };
            }
            state.isLoading = false;
          });
        } catch (error: any) {
          set((state) => {
            state.isLoading = false;
            state.error = error.message || "Update failed";
          });
          throw error;
        }
      },

      // Clear error
      clearError: () =>
        set((state) => {
          state.error = null;
        }),
    })),
    {
      name: "auth-storage",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// =============================================================================
// SELECTORS
// =============================================================================

export const selectUser = (state: AuthState) => state.user;
export const selectIsAuthenticated = (state: AuthState) => state.isAuthenticated;
export const selectIsLoading = (state: AuthState) => state.isLoading;
export const selectError = (state: AuthState) => state.error;
export const selectAccessToken = (state: AuthState) => state.accessToken;
