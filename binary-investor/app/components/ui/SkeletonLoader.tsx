"use client";

import React from "react";

export default function SkeletonLoader() {
  return (
    <div className="w-full space-y-8 animate-pulse">
      {/* Hero Card Skeleton */}
      <div className="bg-surface-container-lowest rounded-2xl p-6 sm:p-8 border border-surface-container-high/60 space-y-6">
        <div className="flex flex-col sm:flex-row justify-between gap-4">
          <div className="space-y-2.5">
            <div className="h-8 w-64 bg-surface-container-high rounded-lg" />
            <div className="h-4 w-96 bg-surface-container rounded-md" />
            <div className="h-10 w-48 bg-surface-container-highest rounded-xl mt-3" />
          </div>
        </div>
        <div className="h-24 w-full bg-surface-container-low rounded-xl" />
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-20 bg-surface-container-low rounded-xl" />
          ))}
        </div>
      </div>

      {/* Gauges Skeleton */}
      <div className="space-y-4">
        <div className="h-6 w-56 bg-surface-container-high rounded-md" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-64 bg-surface-container-lowest rounded-2xl p-6 border border-surface-container-high/60 flex flex-col items-center justify-between"
            >
              <div className="h-5 w-32 bg-surface-container rounded-md" />
              <div className="w-40 h-24 bg-surface-container-low rounded-full" />
              <div className="h-10 w-full bg-surface-container rounded-lg" />
            </div>
          ))}
        </div>
      </div>

      {/* Chart Skeleton */}
      <div className="h-96 bg-surface-container-lowest rounded-2xl border border-surface-container-high/60 p-6" />
    </div>
  );
}
