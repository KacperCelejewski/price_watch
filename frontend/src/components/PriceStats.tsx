"use client";

import type { PriceStats } from "@/lib/api";

interface PriceStatsProps {
  stats: PriceStats;
}

interface StatCardProps {
  label: string;
  value: string | null;
  color: string;
}

function StatCard({ label, value, color }: StatCardProps) {
  return (
    <div className={`bg-white dark:bg-slate-800 rounded-xl border ${color} p-4`}>
      <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">
        {label}
      </p>
      <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">
        {value ?? "—"}
      </p>
    </div>
  );
}

export default function PriceStats({ stats }: PriceStatsProps) {
  const fmt = (v: number | null) => (v != null ? `${v.toFixed(2)} PLN` : null);

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <StatCard
        label="Lowest"
        value={fmt(stats.min_price)}
        color="border-green-200 dark:border-green-800"
      />
      <StatCard
        label="Highest"
        value={fmt(stats.max_price)}
        color="border-red-200 dark:border-red-800"
      />
      <StatCard
        label="Average"
        value={fmt(stats.avg_price)}
        color="border-blue-200 dark:border-blue-800"
      />
      <StatCard
        label="Data Points"
        value={stats.count != null ? String(stats.count) : null}
        color="border-slate-200 dark:border-slate-700"
      />
    </div>
  );
}
