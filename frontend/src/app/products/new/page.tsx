"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import toast from "react-hot-toast";
import { ArrowLeft, Loader2 } from "lucide-react";
import { createProduct, triggerScrape } from "@/lib/api";

const CATEGORIES = [
  "Electronics",
  "Home & Garden",
  "Sport & Outdoors",
  "Clothing & Fashion",
  "Books & Media",
  "Toys & Games",
  "Food & Beverages",
  "Health & Beauty",
  "Automotive",
  "Other",
];

export default function NewProductPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    url: "",
    name: "",
    shop: "",
    category: "",
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.url || !form.name) {
      toast.error("URL and name are required");
      return;
    }
    setLoading(true);
    try {
      const product = await createProduct({
        url: form.url.trim(),
        name: form.name.trim(),
        shop: form.shop.trim() || undefined,
        category: form.category || undefined,
      });
      toast.success("Product added! Scraping price now...");

      // Trigger immediate price scrape
      try {
        const result = await triggerScrape(product.id);
        if (result.scraped_price != null) {
          toast.success(`First price scraped: ${result.scraped_price.toFixed(2)} PLN`);
        }
      } catch {
        // Non-fatal: product is added, just no price yet
      }

      router.push(`/products/${product.id}`);
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Failed to add product";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8">
      <div className="flex items-center gap-3 mb-6">
        <Link
          href="/"
          className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
        >
          <ArrowLeft size={20} />
        </Link>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Add New Product</h1>
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Product URL <span className="text-red-500">*</span>
            </label>
            <input
              name="url"
              type="url"
              required
              value={form.url}
              onChange={handleChange}
              placeholder="https://www.ceneo.pl/..."
              className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            />
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
              Supports Ceneo, Allegro, or any shop with a visible price
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Product Name <span className="text-red-500">*</span>
            </label>
            <input
              name="name"
              type="text"
              required
              value={form.name}
              onChange={handleChange}
              placeholder="e.g. Apple iPhone 15 128GB"
              className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Shop (optional)
              </label>
              <input
                name="shop"
                type="text"
                value={form.shop}
                onChange={handleChange}
                placeholder="e.g. Ceneo"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Category (optional)
              </label>
              <select
                name="category"
                value={form.category}
                onChange={handleChange}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              >
                <option value="">Select category</option>
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white py-2 px-4 rounded-lg font-medium transition-colors"
            >
              {loading && <Loader2 size={16} className="animate-spin" />}
              {loading ? "Adding..." : "Add Product & Scrape Price"}
            </button>
            <Link
              href="/"
              className="px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 font-medium transition-colors text-sm flex items-center"
            >
              Cancel
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
