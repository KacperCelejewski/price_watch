"use client";

import { useState } from "react";
import toast from "react-hot-toast";
import { Loader2 } from "lucide-react";
import { createAlert } from "@/lib/api";
import type { Product } from "@/lib/api";

interface AlertFormProps {
  products: Product[];
  onCreated: () => void;
}

export default function AlertForm({ products, onCreated }: AlertFormProps) {
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    product_id: "",
    user_email: "",
    threshold_price: "",
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.product_id || !form.user_email || !form.threshold_price) {
      toast.error("All fields are required");
      return;
    }
    const threshold = parseFloat(form.threshold_price);
    if (isNaN(threshold) || threshold <= 0) {
      toast.error("Enter a valid threshold price");
      return;
    }
    setLoading(true);
    try {
      await createAlert({
        product_id: Number(form.product_id),
        user_email: form.user_email.trim(),
        threshold_price: threshold,
      });
      toast.success("Alert created successfully");
      setForm({ product_id: "", user_email: "", threshold_price: "" });
      onCreated();
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Failed to create alert";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
          Product <span className="text-red-500">*</span>
        </label>
        <select
          name="product_id"
          value={form.product_id}
          onChange={handleChange}
          required
          className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
        >
          <option value="">Select a product</option>
          {products.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
          Email <span className="text-red-500">*</span>
        </label>
        <input
          name="user_email"
          type="email"
          required
          value={form.user_email}
          onChange={handleChange}
          placeholder="you@example.com"
          className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
          Alert when price drops below (PLN) <span className="text-red-500">*</span>
        </label>
        <input
          name="threshold_price"
          type="number"
          min="0.01"
          step="0.01"
          required
          value={form.threshold_price}
          onChange={handleChange}
          placeholder="e.g. 999.99"
          className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white py-2 px-4 rounded-lg font-medium transition-colors text-sm"
      >
        {loading && <Loader2 size={14} className="animate-spin" />}
        {loading ? "Creating..." : "Create Alert"}
      </button>
    </form>
  );
}
