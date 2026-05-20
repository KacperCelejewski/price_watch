import axios from "axios";

export const apiClient = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

// Types
export interface Product {
  id: number;
  name: string;
  url: string;
  shop: string | null;
  category: string | null;
  created_at: string;
}

export interface ProductWithPrices extends Product {
  prices: PriceHistory[];
}

export interface PriceHistory {
  id: number;
  product_id: number;
  price: number;
  currency: string;
  scraped_at: string;
}

export interface PriceStats {
  product_id: number;
  days: number;
  min_price: number | null;
  max_price: number | null;
  avg_price: number | null;
  current_price: number | null;
  count: number;
}

export interface PredictionForecast {
  date: string;
  predicted_price: number;
}

export interface Prediction {
  product_id: number;
  product_name: string;
  days: number;
  forecast: PredictionForecast[];
  current_price: number;
  training_samples: number;
}

export interface Recommendation {
  product_id: number;
  product_name: string;
  action: "buy" | "wait" | "watch";
  confidence: number;
  reason: string;
  predicted_min_price: number | null;
  days_to_min: number | null;
}

export interface Alert {
  id: number;
  product_id: number;
  user_email: string;
  threshold_price: number;
  is_active: boolean;
  created_at: string;
}

export interface ProductCreate {
  name: string;
  url: string;
  shop?: string;
  category?: string;
}

export interface AlertCreate {
  product_id: number;
  user_email: string;
  threshold_price: number;
}

// API functions
export const getProducts = async (params?: { name?: string; category?: string }): Promise<Product[]> => {
  const { data } = await apiClient.get<Product[]>("/products", { params });
  return data;
};

export const getProduct = async (id: number): Promise<ProductWithPrices> => {
  const { data } = await apiClient.get<ProductWithPrices>(`/products/${id}`);
  return data;
};

export const createProduct = async (product: ProductCreate): Promise<Product> => {
  const { data } = await apiClient.post<Product>("/products", product);
  return data;
};

export const deleteProduct = async (id: number): Promise<void> => {
  await apiClient.delete(`/products/${id}`);
};

export const getPrices = async (productId: number, days = 30): Promise<PriceHistory[]> => {
  const { data } = await apiClient.get<PriceHistory[]>(`/products/${productId}/prices`, {
    params: { days },
  });
  return data;
};

export const getStats = async (productId: number, days = 30): Promise<PriceStats> => {
  const { data } = await apiClient.get<PriceStats>(`/products/${productId}/prices/stats`, {
    params: { days },
  });
  return data;
};

export const getPrediction = async (productId: number, days = 7): Promise<Prediction> => {
  const { data } = await apiClient.get<Prediction>(`/products/${productId}/predict`, {
    params: { days },
  });
  return data;
};

export const getRecommendation = async (productId: number): Promise<Recommendation> => {
  const { data } = await apiClient.get<Recommendation>(`/products/${productId}/recommendation`);
  return data;
};

export const createAlert = async (alert: AlertCreate): Promise<Alert> => {
  const { data } = await apiClient.post<Alert>("/alerts", alert);
  return data;
};

export const getAlerts = async (params?: { product_id?: number; is_active?: boolean }): Promise<Alert[]> => {
  const { data } = await apiClient.get<Alert[]>("/alerts", { params });
  return data;
};

export const deleteAlert = async (id: number): Promise<void> => {
  await apiClient.delete(`/alerts/${id}`);
};

export const triggerScrape = async (productId: number): Promise<{ scraped_price: number | null; status: string }> => {
  const { data } = await apiClient.post(`/scraper/trigger/${productId}`);
  return data;
};
