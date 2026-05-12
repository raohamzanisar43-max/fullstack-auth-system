import axios, { AxiosInstance, AxiosResponse } from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  error?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  username: string;
  confirm_password: string;
  full_name: string;
}

export interface AuthResponse {
  id: number;
  email: string;
  username: string;
  full_name: string;
  phone?: string;
  company?: string;
  bio?: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
  role: string;
  created_at: string;
  updated_at: string;
  last_login?: string;
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  phone?: string;
  company?: string;
  bio?: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
  role: string;
  created_at: string;
  updated_at: string;
  last_login?: string;
}

export interface TraceJob {
  id: number;
  user_id: number;
  name: string;
  type: "normal" | "enhanced";
  status: "pending" | "processing" | "completed" | "failed";
  total_records: number;
  processed_records: number;
  successful_records: number;
  credits_used: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  file_path?: string;
  result_file_path?: string;
}

export interface ManualSearch {
  id: number;
  user_id: number;
  search_type: "property" | "owner" | "phone" | "email";
  search_query: string;
  results: any[];
  credits_used: number;
  status: "pending" | "completed" | "failed";
  created_at: string;
  updated_at: string;
}

export interface CreditBalance {
  credits: number;
  credit_rate: number;
  total_used: number;
  last_recharge?: string;
}

export interface DashboardStats {
  lists_uploaded: number;
  properties_uploaded: number;
  successful_traces: number;
  credits_used: number;
  success_rate: number;
}

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Add request interceptor to include auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem("access_token");
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      },
    );

    // Add response interceptor to handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem("refresh_token");
            if (refreshToken) {
              const response = await this.client.post("/auth/refresh", {
                refresh_token: refreshToken,
              });

              const { access_token, refresh_token: newRefreshToken } =
                response.data;
              localStorage.setItem("access_token", access_token);
              localStorage.setItem("refresh_token", newRefreshToken);

              // Retry the original request
              originalRequest.headers.Authorization = `Bearer ${access_token}`;
              return this.client(originalRequest);
            }
          } catch (refreshError) {
            // Refresh failed, logout user
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            window.location.href = "/login";
          }
        }

        return Promise.reject(error);
      },
    );
  }

  // Authentication endpoints
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response: AxiosResponse<AuthResponse> = await this.client.post(
      "/auth/login",
      data,
    );
    return response.data;
  }

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response: AxiosResponse<AuthResponse> = await this.client.post(
      "/auth/register",
      data,
    );
    return response.data;
  }

  async logout(): Promise<void> {
    await this.client.post("/auth/logout");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.client.get("/auth/me");
    return response.data;
  }

  async refreshToken(
    refreshToken: string,
  ): Promise<{ access_token: string; refresh_token: string }> {
    const response = await this.client.post("/auth/refresh", {
      refresh_token: refreshToken,
    });
    return response.data;
  }

  // Trace job endpoints
  async createTraceJob(data: {
    name: string;
    type: string;
    file: File;
    column_mapping?: Record<string, string>;
  }): Promise<TraceJob> {
    const formData = new FormData();
    formData.append("name", data.name);
    formData.append("type", data.type);
    formData.append("file", data.file);
    if (data.column_mapping) {
      formData.append("column_mapping", JSON.stringify(data.column_mapping));
    }

    const response: AxiosResponse<TraceJob> = await this.client.post(
      "/traces/",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      },
    );
    return response.data;
  }

  async getTraceJobs(): Promise<TraceJob[]> {
    const response: AxiosResponse<TraceJob[]> =
      await this.client.get("/traces/");
    return response.data;
  }

  async getTraceJob(id: number): Promise<TraceJob> {
    const response: AxiosResponse<TraceJob> = await this.client.get(
      `/traces/${id}`,
    );
    return response.data;
  }

  async deleteTraceJob(id: number): Promise<void> {
    await this.client.delete(`/traces/${id}`);
  }

  async downloadTraceResults(id: number): Promise<Blob> {
    const response = await this.client.get(`/traces/${id}/download`, {
      responseType: "blob",
    });
    return response.data;
  }

  // Manual search endpoints
  async createManualSearch(data: any): Promise<ManualSearch> {
    const response: AxiosResponse<ManualSearch> = await this.client.post(
      "/traces/manual-search",
      data,
    );
    return response.data;
  }

  async getManualSearches(): Promise<ManualSearch[]> {
    const response: AxiosResponse<ManualSearch[]> = await this.client.get(
      "/traces/manual-search",
    );
    return response.data;
  }

  // Credits endpoints
  async getCreditBalance(): Promise<CreditBalance> {
    const response: AxiosResponse<CreditBalance> =
      await this.client.get("/credits/balance");
    return response.data;
  }

  async purchaseCredits(data: any): Promise<any> {
    const response = await this.client.post("/credits/purchase", data);
    return response.data;
  }

  async getCreditTransactions(): Promise<any[]> {
    const response = await this.client.get("/credits/transactions");
    return response.data;
  }

  // Dashboard endpoints
  async getDashboardStats(): Promise<DashboardStats> {
    const response: AxiosResponse<DashboardStats> =
      await this.client.get("/dashboard/stats");
    return response.data;
  }

  async getDashboardActivity(): Promise<any[]> {
    const response = await this.client.get("/dashboard/activity");
    return response.data;
  }

  // DNC endpoints
  async createDncScrub(data: any): Promise<any> {
    const response = await this.client.post("/dnc/", data);
    return response.data;
  }

  async getDncScrubs(): Promise<any[]> {
    const response = await this.client.get("/dnc/");
    return response.data;
  }
}

export const apiClient = new ApiClient();
export default apiClient;
