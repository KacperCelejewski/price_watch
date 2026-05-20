"use client";

import "./globals.css";
import { Toaster } from "react-hot-toast";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import Link from "next/link";
import NotificationBanner from "@/components/NotificationBanner";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000,
        retry: 1,
      },
    },
  }));

  return (
    <html lang="en">
      <head>
        <title>Price Watch</title>
        <meta name="description" content="Track product prices and get shopping recommendations" />
      </head>
      <body>
        <QueryClientProvider client={queryClient}>
          <nav className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex items-center justify-between h-16">
                <Link href="/" className="flex items-center gap-2 font-bold text-xl text-blue-600">
                  <span>Price Watch</span>
                </Link>
                <div className="flex items-center gap-6 text-sm font-medium text-slate-600 dark:text-slate-300">
                  <Link href="/" className="hover:text-blue-600 transition-colors">Dashboard</Link>
                  <Link href="/products/new" className="hover:text-blue-600 transition-colors">Add Product</Link>
                  <Link href="/alerts" className="hover:text-blue-600 transition-colors">Alerts</Link>
                  <Link href="/settings" className="hover:text-blue-600 transition-colors">Settings</Link>
                </div>
              </div>
            </div>
          </nav>
          <NotificationBanner />
          <main className="min-h-screen bg-slate-50 dark:bg-slate-950">
            {children}
          </main>
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: "#1e293b",
                color: "#f8fafc",
                borderRadius: "8px",
                fontSize: "14px",
              },
            }}
          />
        </QueryClientProvider>
      </body>
    </html>
  );
}
