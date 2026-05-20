"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import type { PriceHistory, PredictionForecast } from "@/lib/api";

interface PriceChartProps {
  history: PriceHistory[];
  predictions?: PredictionForecast[];
}

interface ChartDataPoint {
  date: string;
  historical?: number;
  predicted?: number;
}

const formatDate = (dateStr: string) => {
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-GB", { day: "2-digit", month: "short" });
};

const formatPrice = (value: number) => `${value.toFixed(2)} PLN`;

export default function PriceChart({ history, predictions = [] }: PriceChartProps) {
  // Build merged dataset
  const histMap: Record<string, number> = {};
  history.forEach((p) => {
    const day = p.scraped_at.slice(0, 10);
    histMap[day] = p.price;
  });

  const predMap: Record<string, number> = {};
  predictions.forEach((p) => {
    predMap[p.date] = p.predicted_price;
  });

  const allDates = Array.from(
    new Set([...Object.keys(histMap), ...Object.keys(predMap)])
  ).sort();

  const data: ChartDataPoint[] = allDates.map((date) => ({
    date,
    historical: histMap[date],
    predicted: predMap[date],
  }));

  const today = new Date().toISOString().slice(0, 10);

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-slate-50 dark:bg-slate-800 rounded-lg text-slate-400 dark:text-slate-500">
        No price data available
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={data} margin={{ top: 8, right: 24, left: 8, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis
          dataKey="date"
          tickFormatter={formatDate}
          tick={{ fontSize: 11, fill: "#94a3b8" }}
          interval="preserveStartEnd"
        />
        <YAxis
          tickFormatter={(v) => `${v.toFixed(0)}`}
          tick={{ fontSize: 11, fill: "#94a3b8" }}
          domain={["auto", "auto"]}
        />
        <Tooltip
          formatter={(value: number, name: string) => [
            formatPrice(value),
            name === "historical" ? "Historical Price" : "Predicted Price",
          ]}
          labelFormatter={(label) => `Date: ${label}`}
          contentStyle={{
            background: "#1e293b",
            border: "none",
            borderRadius: "8px",
            color: "#f8fafc",
            fontSize: "13px",
          }}
        />
        <Legend
          formatter={(value) =>
            value === "historical" ? "Historical Price" : "Predicted Price"
          }
          wrapperStyle={{ fontSize: "12px" }}
        />
        {today && <ReferenceLine x={today} stroke="#94a3b8" strokeDasharray="4 2" label="" />}
        <Line
          type="monotone"
          dataKey="historical"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 4 }}
          connectNulls={false}
        />
        {predictions.length > 0 && (
          <Line
            type="monotone"
            dataKey="predicted"
            stroke="#f97316"
            strokeWidth={2}
            strokeDasharray="6 3"
            dot={false}
            activeDot={{ r: 4 }}
            connectNulls={false}
          />
        )}
      </LineChart>
    </ResponsiveContainer>
  );
}
