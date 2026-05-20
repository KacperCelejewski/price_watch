"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Plus, TrendingDown, Package, Bell } from "lucide-react";
import { getProducts, getPrices, getRecommendation } from "@/lib/api";
import ProductCard from "@/components/ProductCard";

export default function DashboardPage() {
  const { data: products = [], isLoading } = useQuery({
    queryKey: ["products"],
    queryFn: () => getProducts(),
  });

  const { data: allPrices = [] } = useQuery({
    queryKey: ["all-prices-dashboard"],
    queryFn: async () => {
      const results = await Promise.allSettled(
        products.slice(0, 20).map((p) => getPrices(p.id, 2))
      );
      return results.map((r, i) => ({
        productId: products[i].id,
        prices: r.status === "fulfilled" ? r.value : [],
      }));
    },
    enabled: products.length > 0,
  });

  const getPriceData = (productId: number) => {
    const entry = allPrices.find((p) => p.productId === productId);
    if (!entry || entry.prices.length === 0) return { latest: null, previous: null };
    const sorted = [...entry.prices].sort(
      (a, b) => new Date(b.scraped_at).getTime() - new Date(a.scraped_at).getTime()
    );
    return {
      latest: sorted[0]?.price ?? null,
      previous: sorted[1]?.price ?? null,
    };
  };

  // Find top price drops
  const priceDrops = allPrices
    .map(({ productId, prices }) => {
      if (prices.length < 2) return null;
      const sorted = [...prices].sort(
        (a, b) => new Date(b.scraped_at).getTime() - new Date(a.scraped_at).getTime()
      );
      const latest = sorted[0].price;
      const prev = sorted[1].price;
      if (prev > 0 && latest < prev) {
        const drop = ((prev - latest) / prev) * 100;
        return { productId, drop, latest };
      }
      return null;
    })
    .filter(Boolean)
    .sort((a, b) => (b?.drop ?? 0) - (a?.drop ?? 0))
    .slice(0, 3);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Dashboard</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">
            Monitor your tracked products and price trends
          </p>
        </div>
        <Link
          href="/products/new"
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
        >
          <Plus size={16} />
          Add Product
        </Link>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <Package size={20} className="text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p className="text-sm text-slate-500 dark:text-slate-400">Total Products</p>
              <p className="text-2xl font-bold text-slate-900 dark:text-white">{products.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <TrendingDown size={20} className="text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p className="text-sm text-slate-500 dark:text-slate-400">Price Drops Today</p>
              <p className="text-2xl font-bold text-slate-900 dark:text-white">{priceDrops.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-orange-100 dark:bg-orange-900 rounded-lg">
              <Bell size={20} className="text-orange-600 dark:text-orange-400" />
            </div>
            <div>
              <p className="text-sm text-slate-500 dark:text-slate-400">Active Alerts</p>
              <Link href="/alerts" className="text-2xl font-bold text-slate-900 dark:text-white hover:text-blue-600 transition-colors">
                View
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Top price drops section */}
      {priceDrops.length > 0 && (
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
            <TrendingDown size={18} className="text-green-500" />
            Top Price Drops Today
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {priceDrops.map((drop) => {
              if (!drop) return null;
              const product = products.find((p) => p.id === drop.productId);
              if (!product) return null;
              return (
                <Link
                  key={drop.productId}
                  href={`/products/${drop.productId}`}
                  className="bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 rounded-xl p-4 hover:border-green-400 transition-colors"
                >
                  <p className="font-medium text-slate-900 dark:text-white text-sm line-clamp-1">{product.name}</p>
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400 mt-1">
                    -{drop.drop.toFixed(1)}%
                  </p>
                  <p className="text-sm text-slate-600 dark:text-slate-300 mt-0.5">
                    Now {drop.latest.toFixed(2)} PLN
                  </p>
                </Link>
              );
            })}
          </div>
        </div>
      )}

      {/* All products */}
      <div>
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
          Tracked Products
        </h2>
        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div
                key={i}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 animate-pulse h-36"
              />
            ))}
          </div>
        ) : products.length === 0 ? (
          <div className="text-center py-16 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
            <Package size={40} className="mx-auto text-slate-300 dark:text-slate-600 mb-3" />
            <p className="text-slate-500 dark:text-slate-400 font-medium">No products tracked yet</p>
            <p className="text-sm text-slate-400 dark:text-slate-500 mt-1 mb-4">
              Add your first product to start monitoring prices
            </p>
            <Link
              href="/products/new"
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors text-sm"
            >
              <Plus size={14} />
              Add Product
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {products.map((product) => {
              const { latest, previous } = getPriceData(product.id);
              return (
                <ProductCard
                  key={product.id}
                  product={product}
                  latestPrice={latest}
                  previousPrice={previous}
                />
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
