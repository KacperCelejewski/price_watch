"use client";

import Link from "next/link";
import { Bell, TrendingDown } from "lucide-react";
import { useAlerts } from "@/hooks/useAlerts";

export default function NotificationBanner() {
  const { alerts, products } = useAlerts();

  const activeAlerts = alerts.filter((a) => a.is_active);
  if (activeAlerts.length === 0) return null;

  return (
    <div className="bg-orange-50 dark:bg-orange-950 border-b border-orange-200 dark:border-orange-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2 flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm text-orange-700 dark:text-orange-300">
          <Bell size={14} className="flex-shrink-0" />
          <span>
            <span className="font-semibold">{activeAlerts.length}</span>{" "}
            active price {activeAlerts.length === 1 ? "alert" : "alerts"} — monitoring prices every 5 minutes
          </span>
        </div>
        <Link
          href="/alerts"
          className="text-xs font-medium text-orange-700 dark:text-orange-300 hover:text-orange-900 dark:hover:text-orange-100 underline"
        >
          Manage alerts
        </Link>
      </div>
    </div>
  );
}
