import axios, { AxiosInstance, AxiosResponse } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

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
  firstName: string;
  lastName: string;
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
  type: 'normal' | 'enhanced';
  status: 'pending' | 'processing' | 'completed' | 'failed';
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
  search_type: 'property' | 'owner' | 'phone' | 'email';
  search_query: string;
  results: any[];
  credits_used: number;
  status: 'pending' | 'completed' | 'failed';
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
  total_credits_used: number;
  effective_rate: number;
  usage_breakdown: {
    normal: { queues: number; credits_used: number };
    enhanced: { queues: number; credits_used: number };
  };
}

export interface DncScrub {
  id: number;
  user_id: number;
  name: string;
  total_records: number;
  clean_records: number;
  dnc_records: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  credits_used: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  file_path?: string;
  result_file_path?: string;
}

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
                refresh_token: refreshToken,
              });

              const { access_token, refresh_token: new_refresh_token } = response.data;
              localStorage.setItem('access_token', access_token);
              localStorage.setItem('refresh_token', new_refresh_token);

              originalRequest.headers.Authorization = `Bearer ${access_token}`;
              return this.client(originalRequest);
            }
          } catch (refreshError) {
            // Refresh failed, logout user
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Authentication endpoints
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response: AxiosResponse<AuthResponse> = await this.client.post('/auth/login', data);
    return response.data;
  }

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response: AxiosResponse<AuthResponse> = await this.client.post('/auth/register', data);
    return response.data;
  }

  async logout(): Promise<void> {
    await this.client.post('/auth/logout');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.client.get('/auth/me');
    return response.data;
  }

  async refreshToken(refreshToken: string): Promise<{ access_token: string; refresh_token: string }> {
    const response = await this.client.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  }

  // Trace job endpoints
  async createTraceJob(data: { name: string; type: 'normal' | 'enhanced'; file: File }): Promise<TraceJob> {
    const formData = new FormData();
    formData.append('name', data.name);
    formData.append('type', data.type);
    formData.append('file', data.file);

    const response: AxiosResponse<TraceJob> = await this.client.post('/traces', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async getTraceJobs(skip = 0, limit = 50): Promise<TraceJob[]> {
    const response: AxiosResponse<TraceJob[]> = await this.client.get(`/traces?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async getTraceJob(id: number): Promise<TraceJob> {
    const response: AxiosResponse<TraceJob> = await this.client.get(`/traces/${id}`);
    return response.data;
  }

  async downloadTraceResults(id: number): Promise<Blob> {
    const response = await this.client.get(`/traces/${id}/download`, {
      responseType: 'blob',
    });
    return response.data;
  }

  // Manual search endpoints
  async createManualSearch(data: { search_type: string; search_query: string }): Promise<ManualSearch> {
    const response: AxiosResponse<ManualSearch> = await this.client.post('/searches', data);
    return response.data;
  }

  async getManualSearches(skip = 0, limit = 50): Promise<ManualSearch[]> {
    const response: AxiosResponse<ManualSearch[]> = await this.client.get(`/searches?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async getManualSearch(id: number): Promise<ManualSearch> {
    const response: AxiosResponse<ManualSearch> = await this.client.get(`/searches/${id}`);
    return response.data;
  }

  // Credit endpoints
  async getCreditBalance(): Promise<CreditBalance> {
    const response: AxiosResponse<CreditBalance> = await this.client.get('/credits/balance');
    return response.data;
  }

  async purchaseCredits(data: { amount: number; payment_method_id: string }): Promise<{ credits: number; transaction_id: string }> {
    const response = await this.client.post('/credits/purchase', data);
    return response.data;
  }

  async getCreditTransactions(skip = 0, limit = 50): Promise<any[]> {
    const response = await this.client.get(`/credits/transactions?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  // Dashboard endpoints
  async getDashboardStats(): Promise<DashboardStats> {
    const response: AxiosResponse<DashboardStats> = await this.client.get('/dashboard/stats');
    return response.data;
  }

  // DNC scrub endpoints
  async createDncScrub(data: { name: string; file: File }): Promise<DncScrub> {
    const formData = new FormData();
    formData.append('name', data.name);
    formData.append('file', data.file);

    const response: AxiosResponse<DncScrub> = await this.client.post('/dnc', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async getDncScrubs(skip = 0, limit = 50): Promise<DncScrub[]> {
    const response: AxiosResponse<DncScrub[]> = await this.client.get(`/dnc?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async getDncScrub(id: number): Promise<DncScrub> {
    const response: AxiosResponse<DncScrub> = await this.client.get(`/dnc/${id}`);
    return response.data;
  }

  async downloadDncResults(id: number): Promise<Blob> {
    const response = await this.client.get(`/dnc/${id}/download`, {
      responseType: 'blob',
    });
    return response.data;
  }

  // County lead lists
  async getCountyLeadLists(): Promise<any[]> {
    const response = await this.client.get('/county-leads');
    return response.data;
  }

  async purchaseCountyLeadList(data: { county: string; state: string }): Promise<{ download_url: string }> {
    const response = await this.client.post('/county-leads/purchase', data);
    return response.data;
  }
}

export const apiClient = new ApiClient();
export default apiClient;
