/**
 * Zustand auth store — persists tokens to localStorage.
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface Practitioner {
  id: number;
  name: string;
  email: string;
  practice_name: string | null;
  practice_logo_url: string | null;
  designation: string | null;
  subscription_tier: string;
  subscription_active: boolean;
  in_trial: boolean;
  trial_ends_at: string | null;
}

interface AuthState {
  practitioner: Practitioner | null;
  access_token: string | null;
  refresh_token: string | null;
  setAuth: (practitioner: Practitioner, access_token: string, refresh_token: string) => void;
  clearAuth: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      practitioner: null,
      access_token: null,
      refresh_token: null,

      setAuth: (practitioner, access_token, refresh_token) => {
        // Also write to localStorage for the axios interceptor
        localStorage.setItem("access_token", access_token);
        localStorage.setItem("refresh_token", refresh_token);
        set({ practitioner, access_token, refresh_token });
      },

      clearAuth: () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        set({ practitioner: null, access_token: null, refresh_token: null });
      },

      isAuthenticated: () => !!get().access_token,
    }),
    {
      name: "dhanvantari-auth",
      partialize: (state) => ({
        practitioner: state.practitioner,
        access_token: state.access_token,
        refresh_token: state.refresh_token,
      }),
    }
  )
);
