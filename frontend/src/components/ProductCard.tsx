"use client";

import Link from "next/link";
import { ExternalLink, TrendingDown, TrendingUp, Minus } from "lucide-react";
import type { Product, PriceHistory, Recommendation } from "@/lib/api";

interface ProductCardProps {
  product: Product;
  latestPrice?: number | null;
  previousPrice?: number | null;
  recommendation?: Recommendation | null;
}

function RecommendationBadge({ action }: { action: "buy" | "wait" | "watch" }) {
  const styles: Record<string, string> = {
    buy: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
    wait: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
    watch: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  };
  const labels: Record<string, string> = {
    buy: "Buy Now",
    wait: "Wait",
    watch: "Watch",
  };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${styles[action]}`}>
      {labels[action]}
    </span>
  );
}

export default function ProductCard({
  product,
  latestPrice,
  previousPrice,
  recommendation,
}: ProductCardProps) {
  const change =
    latestPrice != null && previousPrice != null && previousPrice > 0
      ? ((latestPrice - previousPrice) / previousPrice) * 100
      : null;

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <Link
            href={`/products/${product.id}`}
            className="font-semibold text-slate-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 line-clamp-2 transition-colors"
          >
            {product.name}
          </Link>
          <div className="flex items-center gap-2 mt-1">
            {product.shop && (
              <span className="text-xs text-slate-500 dark:text-slate-400">{product.shop}</span>
            )}
            {product.category && (
              <span className="text-xs bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 px-2 py-0.5 rounded">
                {product.category}
              </span>
            )}
          </div>
        </div>
        <a
          href={product.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-slate-400 hover:text-blue-500 transition-colors flex-shrink-0"
          aria-label="Open product URL"
        >
          <ExternalLink size={16} />
        </a>
      </div>

      <div className="mt-4 flex items-end justify-between">
        <div>
          {latestPrice != null ? (
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold text-slate-900 dark:text-white">
                {latestPrice.toFixed(2)} PLN
              </span>
              {change !== null && (
                <span
                  className={`flex items-center gap-0.5 text-sm font-medium ${
                    change < 0
                      ? "text-green-600 dark:text-green-400"
                      : change > 0
                      ? "text-red-500 dark:text-red-400"
                      : "text-slate-400"
                  }`}
                >
                  {change < 0 ? (
                    <TrendingDown size={14} />
                  ) : change > 0 ? (
                    <TrendingUp size={14} />
                  ) : (
                    <Minus size={14} />
                  )}
                  {Math.abs(change).toFixed(1)}%
                </span>
              )}
            </div>
          ) : (
            <span className="text-sm text-slate-400 dark:text-slate-500">No price yet</span>
          )}
        </div>
        {recommendation && <RecommendationBadge action={recommendation.action} />}
      </div>
    </div>
  );
}
