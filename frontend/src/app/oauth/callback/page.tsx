"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

function parseHash(hash: string): Record<string, string> {
  const clean = hash.startsWith("#") ? hash.slice(1) : hash;
  const params = new URLSearchParams(clean);
  const out: Record<string, string> = {};
  params.forEach((v, k) => (out[k] = v));
  return out;
}

export default function OAuthCallbackPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const run = async () => {
      try {
        const { access_token, refresh_token } = parseHash(window.location.hash);

        if (!access_token || !refresh_token) {
          setError("OAuth callback missing tokens. Please try again.");
          return;
        }

        // Save tokens to Zustand (persisted)
        useAuthStore.getState().setTokens(access_token, refresh_token);

        // Clear fragment from URL ASAP
        window.history.replaceState({}, document.title, "/oauth/callback");

        // Fetch user profile
        const res = await fetch(`${API_BASE_URL}/auth/me`, {
          headers: {
            Authorization: `Bearer ${access_token}`,
          },
        });

        if (!res.ok) {
          throw new Error("Failed to load profile after OAuth");
        }

        const user = await res.json();
        useAuthStore.getState().setUser(user);

        // Redirect by role
        const role = user?.role;
        const roleRoot = role === "company" ? "/company" : role === "admin" ? "/admin" : "/student";
        router.replace(roleRoot);
      } catch (e: any) {
        setError(e?.message || "OAuth login failed");
      }
    };

    run();
  }, [router]);

  if (error) {
    return (
      <div className="mx-auto max-w-md p-8">
        <h1 className="text-xl font-semibold">OAuth Login Failed</h1>
        <p className="mt-2 text-sm text-surface-600">{error}</p>
        <button
          className="mt-6 rounded-lg bg-purple-600 px-4 py-2 text-white"
          onClick={() => router.replace("/login")}
        >
          Back to Login
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-md p-8">
      <h1 className="text-xl font-semibold">Signing you in…</h1>
      <p className="mt-2 text-sm text-surface-600">Completing OAuth login and loading your profile.</p>
    </div>
  );
}


