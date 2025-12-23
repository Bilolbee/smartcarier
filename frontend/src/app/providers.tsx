/**
 * =============================================================================
 * APP PROVIDERS
 * =============================================================================
 * 
 * Client-side providers wrapper
 */

"use client";

import { TranslationProvider } from "@/contexts/TranslationContext";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <TranslationProvider>
      {children}
    </TranslationProvider>
  );
}

export default Providers;













