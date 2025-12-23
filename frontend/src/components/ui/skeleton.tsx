/**
 * =============================================================================
 * SKELETON COMPONENT
 * =============================================================================
 */

"use client";

import { cn } from "@/lib/utils";

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "text" | "circular" | "rectangular";
  animation?: "pulse" | "wave" | "none";
}

function Skeleton({
  className,
  variant = "rectangular",
  animation = "pulse",
  ...props
}: SkeletonProps) {
  const variantClasses = {
    text: "rounded",
    circular: "rounded-full",
    rectangular: "rounded-xl",
  };

  const animationClasses = {
    pulse: "animate-pulse",
    wave: "animate-shimmer",
    none: "",
  };

  return (
    <div
      className={cn(
        "bg-surface-200 dark:bg-surface-700",
        variantClasses[variant],
        animationClasses[animation],
        className
      )}
      {...props}
    />
  );
}

// Pre-made skeleton components
function TextSkeleton({ className, lines = 3 }: { className?: string; lines?: number }) {
  return (
    <div className={cn("space-y-2", className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          variant="text"
          className={cn("h-4", i === lines - 1 && "w-3/4")}
        />
      ))}
    </div>
  );
}

function CardSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn("rounded-xl border border-surface-200 p-6", className)}>
      <div className="flex items-start justify-between">
        <div className="flex gap-4">
          <Skeleton variant="circular" className="h-12 w-12" />
          <div className="space-y-2">
            <Skeleton variant="text" className="h-5 w-32" />
            <Skeleton variant="text" className="h-4 w-24" />
          </div>
        </div>
        <Skeleton variant="rectangular" className="h-6 w-16" />
      </div>
      <div className="mt-4 space-y-2">
        <Skeleton variant="text" className="h-4 w-full" />
        <Skeleton variant="text" className="h-4 w-full" />
        <Skeleton variant="text" className="h-4 w-2/3" />
      </div>
      <div className="mt-4 flex gap-2">
        <Skeleton variant="rectangular" className="h-6 w-16" />
        <Skeleton variant="rectangular" className="h-6 w-16" />
        <Skeleton variant="rectangular" className="h-6 w-16" />
      </div>
    </div>
  );
}

function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex gap-4 border-b border-surface-200 pb-3">
        <Skeleton variant="text" className="h-4 w-32" />
        <Skeleton variant="text" className="h-4 w-24" />
        <Skeleton variant="text" className="h-4 w-20" />
        <Skeleton variant="text" className="h-4 w-28" />
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 py-2">
          <Skeleton variant="text" className="h-4 w-32" />
          <Skeleton variant="text" className="h-4 w-24" />
          <Skeleton variant="text" className="h-4 w-20" />
          <Skeleton variant="text" className="h-4 w-28" />
        </div>
      ))}
    </div>
  );
}

function ProfileSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn("flex flex-col items-center", className)}>
      <Skeleton variant="circular" className="h-24 w-24" />
      <Skeleton variant="text" className="mt-4 h-6 w-32" />
      <Skeleton variant="text" className="mt-2 h-4 w-48" />
      <div className="mt-4 flex gap-2">
        <Skeleton variant="rectangular" className="h-8 w-20" />
        <Skeleton variant="rectangular" className="h-8 w-20" />
      </div>
    </div>
  );
}

export {
  Skeleton,
  TextSkeleton,
  CardSkeleton,
  TableSkeleton,
  ProfileSkeleton,
};
