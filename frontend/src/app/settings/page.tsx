"use client";

import { useState, useEffect } from "react";
import toast from "react-hot-toast";
import { Settings, Moon, Sun, Bell, Clock, Mail, Loader2 } from "lucide-react";
import { apiClient } from "@/lib/api";

type ScrapeInterval = "1" | "6" | "12" | "24";

interface UserSettings {
  email: string;
  scrapeInterval: ScrapeInterval;
  notifyOnDrop: boolean;
  notifyOnAnomaly: boolean;
  notifyOnRecommendation: boolean;
  darkMode: boolean;
}

const DEFAULT_SETTINGS: UserSettings = {
  email: "",
  scrapeInterval: "6",
  notifyOnDrop: true,
  notifyOnAnomaly: false,
  notifyOnRecommendation: true,
  darkMode: false,
};

const STORAGE_KEY = "price-watch-settings";

function loadSettings(): UserSettings {
  if (typeof window === "undefined") return DEFAULT_SETTINGS;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? { ...DEFAULT_SETTINGS, ...JSON.parse(raw) } : DEFAULT_SETTINGS;
  } catch {
    return DEFAULT_SETTINGS;
  }
}

function saveSettings(settings: UserSettings) {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
  // Apply dark mode
  if (settings.darkMode) {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<UserSettings>(DEFAULT_SETTINGS);
  const [saving, setSaving] = useState(false);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const s = loadSettings();
    setSettings(s);
    if (s.darkMode) document.documentElement.classList.add("dark");
    setLoaded(true);
  }, []);

  const update = <K extends keyof UserSettings>(key: K, value: UserSettings[K]) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    saveSettings(settings);
    try {
      // Best-effort sync to backend (may 404 if user endpoint not fully configured)
      await apiClient.patch("/users/settings", {
        scrape_interval_hours: parseInt(settings.scrapeInterval),
        email: settings.email,
        notify_on_drop: settings.notifyOnDrop,
        notify_on_anomaly: settings.notifyOnAnomaly,
        notify_on_recommendation: settings.notifyOnRecommendation,
        dark_mode: settings.darkMode,
      });
    } catch {
      // Non-fatal — settings are saved to localStorage regardless
    }
    toast.success("Settings saved");
    setSaving(false);
  };

  if (!loaded) return null;

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      <div className="flex items-center gap-3">
        <Settings size={24} className="text-slate-600 dark:text-slate-400" />
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Settings</h1>
      </div>

      {/* Scraping */}
      <section className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 space-y-4">
        <h2 className="font-semibold text-slate-900 dark:text-white flex items-center gap-2">
          <Clock size={16} />
          Scraping Interval
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          How often should we check product prices?
        </p>
        <div className="grid grid-cols-4 gap-2">
          {(["1", "6", "12", "24"] as ScrapeInterval[]).map((h) => (
            <button
              key={h}
              onClick={() => update("scrapeInterval", h)}
              className={`py-2 rounded-lg text-sm font-medium transition-colors ${
                settings.scrapeInterval === h
                  ? "bg-blue-600 text-white"
                  : "bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600"
              }`}
            >
              {h}h
            </button>
          ))}
        </div>
      </section>

      {/* Email */}
      <section className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 space-y-4">
        <h2 className="font-semibold text-slate-900 dark:text-white flex items-center gap-2">
          <Mail size={16} />
          Notification Email
        </h2>
        <input
          type="email"
          value={settings.email}
          onChange={(e) => update("email", e.target.value)}
          placeholder="you@example.com"
          className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
        />
      </section>

      {/* Notification preferences */}
      <section className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 space-y-4">
        <h2 className="font-semibold text-slate-900 dark:text-white flex items-center gap-2">
          <Bell size={16} />
          Notification Preferences
        </h2>
        <div className="space-y-3">
          {[
            {
              key: "notifyOnDrop" as const,
              label: "Price drop alerts",
              desc: "Notify when price drops below your threshold",
            },
            {
              key: "notifyOnAnomaly" as const,
              label: "Anomaly detection",
              desc: "Notify on unusual price spikes or drops",
            },
            {
              key: "notifyOnRecommendation" as const,
              label: "Buy recommendations",
              desc: "Notify when a product hits the ideal buy moment",
            },
          ].map(({ key, label, desc }) => (
            <label key={key} className="flex items-start gap-3 cursor-pointer group">
              <div className="relative mt-0.5">
                <input
                  type="checkbox"
                  checked={settings[key]}
                  onChange={(e) => update(key, e.target.checked)}
                  className="sr-only"
                />
                <div
                  onClick={() => update(key, !settings[key])}
                  className={`w-10 h-6 rounded-full transition-colors cursor-pointer ${
                    settings[key] ? "bg-blue-600" : "bg-slate-200 dark:bg-slate-600"
                  }`}
                >
                  <div
                    className={`w-4 h-4 bg-white rounded-full shadow-sm absolute top-1 transition-transform ${
                      settings[key] ? "translate-x-5" : "translate-x-1"
                    }`}
                  />
                </div>
              </div>
              <div>
                <p className="text-sm font-medium text-slate-900 dark:text-white">{label}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400">{desc}</p>
              </div>
            </label>
          ))}
        </div>
      </section>

      {/* Dark mode */}
      <section className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {settings.darkMode ? (
              <Moon size={16} className="text-slate-600 dark:text-slate-400" />
            ) : (
              <Sun size={16} className="text-slate-600 dark:text-slate-400" />
            )}
            <div>
              <p className="font-semibold text-slate-900 dark:text-white text-sm">Dark Mode</p>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {settings.darkMode ? "Currently using dark theme" : "Currently using light theme"}
              </p>
            </div>
          </div>
          <div
            onClick={() => update("darkMode", !settings.darkMode)}
            className={`w-12 h-7 rounded-full transition-colors cursor-pointer relative ${
              settings.darkMode ? "bg-blue-600" : "bg-slate-200 dark:bg-slate-600"
            }`}
          >
            <div
              className={`w-5 h-5 bg-white rounded-full shadow-sm absolute top-1 transition-transform ${
                settings.darkMode ? "translate-x-6" : "translate-x-1"
              }`}
            />
          </div>
        </div>
      </section>

      <button
        onClick={handleSave}
        disabled={saving}
        className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white py-3 px-4 rounded-xl font-medium transition-colors"
      >
        {saving && <Loader2 size={16} className="animate-spin" />}
        {saving ? "Saving..." : "Save Settings"}
      </button>
    </div>
  );
}
