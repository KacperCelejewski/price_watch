"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { Bell, Trash2, Plus, Package } from "lucide-react";
import { getAlerts, getProducts, deleteAlert } from "@/lib/api";
import AlertForm from "@/components/AlertForm";

export default function AlertsPage() {
  const queryClient = useQueryClient();

  const { data: alerts = [], isLoading: loadingAlerts } = useQuery({
    queryKey: ["alerts"],
    queryFn: () => getAlerts(),
  });

  const { data: products = [] } = useQuery({
    queryKey: ["products"],
    queryFn: () => getProducts(),
  });

  const handleDelete = async (id: number) => {
    try {
      await deleteAlert(id);
      toast.success("Alert deleted");
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    } catch {
      toast.error("Failed to delete alert");
    }
  };

  const handleAlertCreated = () => {
    queryClient.invalidateQueries({ queryKey: ["alerts"] });
  };

  const getProductName = (productId: number) =>
    products.find((p) => p.id === productId)?.name ?? `Product #${productId}`;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
          <Bell size={28} className="text-orange-500" />
          Price Alerts
        </h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">
          Get notified when a product drops below your target price
        </p>
      </div>

      {/* Create alert form */}
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
        <h2 className="font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
          <Plus size={16} />
          New Alert
        </h2>
        {products.length === 0 ? (
          <p className="text-sm text-slate-500 dark:text-slate-400">
            No products tracked yet.{" "}
            <a href="/products/new" className="text-blue-600 hover:underline">
              Add a product first.
            </a>
          </p>
        ) : (
          <AlertForm products={products} onCreated={handleAlertCreated} />
        )}
      </div>

      {/* Alerts list */}
      <div>
        <h2 className="font-semibold text-slate-900 dark:text-white mb-4">
          Active Alerts ({alerts.filter((a) => a.is_active).length})
        </h2>

        {loadingAlerts ? (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div
                key={i}
                className="h-16 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 animate-pulse"
              />
            ))}
          </div>
        ) : alerts.length === 0 ? (
          <div className="text-center py-12 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
            <Bell size={36} className="mx-auto text-slate-300 dark:text-slate-600 mb-3" />
            <p className="text-slate-500 dark:text-slate-400 font-medium">No alerts yet</p>
            <p className="text-sm text-slate-400 dark:text-slate-500 mt-1">
              Create your first alert above to start tracking price drops
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 flex items-center justify-between gap-4"
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div
                    className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${
                      alert.is_active ? "bg-green-400" : "bg-slate-300"
                    }`}
                  />
                  <div className="min-w-0">
                    <p className="font-medium text-slate-900 dark:text-white truncate text-sm">
                      {getProductName(alert.product_id)}
                    </p>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                      Alert when price &lt;{" "}
                      <span className="font-semibold text-slate-700 dark:text-slate-300">
                        {alert.threshold_price.toFixed(2)} PLN
                      </span>{" "}
                      · {alert.user_email}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(alert.id)}
                  className="text-slate-400 hover:text-red-500 transition-colors flex-shrink-0"
                  aria-label="Delete alert"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
