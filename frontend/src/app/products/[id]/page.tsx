"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import toast from "react-hot-toast";
import {
  ArrowLeft,
  ExternalLink,
  RefreshCw,
  ShoppingCart,
  Clock,
  TrendingDown,
} from "lucide-react";
import {
  getProduct,
  getPrices,
  getStats,
  getPrediction,
  getRecommendation,
  triggerScrape,
} from "@/lib/api";
import PriceChart from "@/components/PriceChart";
import PriceStats from "@/components/PriceStats";

type DayRange = 30 | 60 | 90;

const ACTION_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  buy: {
    bg: "bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800",
    text: "text-green-700 dark:text-green-300",
    label: "Buy Now",
  },
  wait: {
    bg: "bg-yellow-50 dark:bg-yellow-950 border-yellow-200 dark:border-yellow-800",
    text: "text-yellow-700 dark:text-yellow-300",
    label: "Wait",
  },
  watch: {
    bg: "bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800",
    text: "text-blue-700 dark:text-blue-300",
    label: "Watch",
  },
};

export default function ProductDetailPage() {
  const params = useParams();
  const router = useRouter();
  const productId = Number(params.id);
  const [days, setDays] = useState<DayRange>(30);
  const [scraping, setScraping] = useState(false);

  const { data: product, isLoading: loadingProduct } = useQuery({
    queryKey: ["product", productId],
    queryFn: () => getProduct(productId),
  });

  const { data: prices = [], refetch: refetchPrices } = useQuery({
    queryKey: ["prices", productId, days],
    queryFn: () => getPrices(productId, days),
    enabled: !!productId,
  });

  const { data: stats, refetch: refetchStats } = useQuery({
    queryKey: ["stats", productId, days],
    queryFn: () => getStats(productId, days),
    enabled: !!productId,
  });

  const { data: prediction } = useQuery({
    queryKey: ["prediction", productId],
    queryFn: () => getPrediction(productId, 14),
    enabled: !!productId,
    retry: false,
  });

  const { data: recommendation } = useQuery({
    queryKey: ["recommendation", productId],
    queryFn: () => getRecommendation(productId),
    enabled: !!productId,
    retry: false,
  });

  const handleScrape = async () => {
    setScraping(true);
    try {
      const result = await triggerScrape(productId);
      if (result.scraped_price != null) {
        toast.success(`Scraped price: ${result.scraped_price.toFixed(2)} PLN`);
        refetchPrices();
        refetchStats();
      } else {
        toast.error("Could not find price on this page");
      }
    } catch {
      toast.error("Scrape failed");
    } finally {
      setScraping(false);
    }
  };

  if (loadingProduct) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-slate-200 dark:bg-slate-700 rounded w-1/3" />
          <div className="h-64 bg-slate-200 dark:bg-slate-700 rounded" />
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-8 text-center">
        <p className="text-slate-500">Product not found.</p>
        <Link href="/" className="text-blue-600 hover:underline mt-4 inline-block">
          Back to dashboard
        </Link>
      </div>
    );
  }

  const actionStyle = recommendation ? ACTION_STYLES[recommendation.action] : null;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Back + header */}
      <div className="flex items-start gap-4">
        <button
          onClick={() => router.back()}
          className="mt-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
        >
          <ArrowLeft size={20} />
        </button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{product.name}</h1>
          <div className="flex flex-wrap items-center gap-3 mt-1">
            {product.shop && (
              <span className="text-sm text-slate-500 dark:text-slate-400">{product.shop}</span>
            )}
            {product.category && (
              <span className="text-xs bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 px-2 py-0.5 rounded">
                {product.category}
              </span>
            )}
            <a
              href={product.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-xs text-blue-600 hover:underline"
            >
              <ExternalLink size={12} />
              View on site
            </a>
          </div>
        </div>
        <button
          onClick={handleScrape}
          disabled={scraping}
          className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 px-3 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
        >
          <RefreshCw size={14} className={scraping ? "animate-spin" : ""} />
          Refresh Price
        </button>
      </div>

      {/* Recommendation card */}
      {recommendation && actionStyle && (
        <div className={`rounded-xl border p-4 ${actionStyle.bg}`}>
          <div className="flex items-center gap-3">
            {recommendation.action === "buy" ? (
              <ShoppingCart size={20} className={actionStyle.text} />
            ) : recommendation.action === "wait" ? (
              <Clock size={20} className={actionStyle.text} />
            ) : (
              <TrendingDown size={20} className={actionStyle.text} />
            )}
            <div>
              <p className={`font-semibold ${actionStyle.text}`}>
                Recommendation: {actionStyle.label}
                {recommendation.confidence != null && (
                  <span className="ml-2 text-sm font-normal opacity-70">
                    ({Math.round(recommendation.confidence * 100)}% confidence)
                  </span>
                )}
              </p>
              <p className="text-sm text-slate-600 dark:text-slate-400 mt-0.5">
                {recommendation.reason}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Stats */}
      {stats && <PriceStats stats={stats} />}

      {/* Chart */}
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-slate-900 dark:text-white">Price History</h2>
          <div className="flex gap-1">
            {([30, 60, 90] as DayRange[]).map((d) => (
              <button
                key={d}
                onClick={() => setDays(d)}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                  days === d
                    ? "bg-blue-600 text-white"
                    : "bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600"
                }`}
              >
                {d}d
              </button>
            ))}
          </div>
        </div>
        <PriceChart history={prices} predictions={prediction?.forecast} />
      </div>
    </div>
  );
}
