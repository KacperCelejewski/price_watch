"use client";

import { useEffect, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { getProducts, getAlerts, getPrices } from "@/lib/api";
import type { Alert, Product, PriceHistory } from "@/lib/api";

const POLL_INTERVAL_MS = 5 * 60 * 1000; // 5 minutes

export function useAlerts() {
  const triggeredRef = useRef<Set<string>>(new Set());

  const { data: products = [] } = useQuery({
    queryKey: ["products"],
    queryFn: getProducts,
    refetchInterval: POLL_INTERVAL_MS,
  });

  const { data: alerts = [] } = useQuery({
    queryKey: ["alerts", { is_active: true }],
    queryFn: () => getAlerts({ is_active: true }),
    refetchInterval: POLL_INTERVAL_MS,
  });

  // For each product that has an active alert, fetch its latest price
  useEffect(() => {
    if (products.length === 0 || alerts.length === 0) return;

    const productIdsWithAlerts = Array.from(new Set(alerts.map((a: Alert) => a.product_id)));

    Promise.allSettled(
      productIdsWithAlerts.map((pid) => getPrices(pid, 1))
    ).then((results) => {
      results.forEach((result, idx) => {
        if (result.status !== "fulfilled") return;
        const productId = productIdsWithAlerts[idx];
        const prices: PriceHistory[] = result.value;
        if (prices.length === 0) return;

        const latestPrice = prices[prices.length - 1].price;
        const product = products.find((p: Product) => p.id === productId);

        const productAlerts = alerts.filter((a: Alert) => a.product_id === productId);
        productAlerts.forEach((alert: Alert) => {
          if (latestPrice <= alert.threshold_price) {
            const key = `${alert.id}:${latestPrice}`;
            if (!triggeredRef.current.has(key)) {
              triggeredRef.current.add(key);
              toast.success(
                `Price drop! ${product?.name ?? `Product #${productId}`} is now ${latestPrice.toFixed(2)} PLN (below your threshold of ${alert.threshold_price.toFixed(2)} PLN)`,
                { duration: 8000 }
              );
            }
          }
        });
      });
    });
  }, [products, alerts]);

  return { alerts, products };
}
