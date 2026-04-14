import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { apiClient, AuthResponse, User } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, username: string, full_name: string, confirm_password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('access_token');
      
      if (token) {
        try {
          const currentUser = await apiClient.getCurrentUser();
          setUser(currentUser);
        } catch (error) {
          // Token is invalid, clear it
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
      
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const authResponse = await apiClient.login({ email, password });
      
      // Store tokens
      localStorage.setItem('access_token', authResponse.access_token);
      localStorage.setItem('refresh_token', authResponse.refresh_token);
      
      // Set user
      const userObj: User = {
        id: authResponse.id,
        email: authResponse.email,
        username: authResponse.username,
        full_name: authResponse.full_name,
        phone: authResponse.phone,
        company: authResponse.company,
        bio: authResponse.bio,
        is_active: authResponse.is_active,
        is_superuser: authResponse.is_superuser,
        is_verified: authResponse.is_verified,
        role: authResponse.role,
        created_at: authResponse.created_at,
        updated_at: authResponse.updated_at,
        last_login: authResponse.last_login,
      };
      
      setUser(userObj);
    } catch (error) {
      throw error;
    }
  };

  const register = async (email: string, password: string, username: string, full_name: string, confirm_password: string) => {
    try {
      const authResponse = await apiClient.register({
        email,
        password,
        username,
        full_name,
        confirm_password,
      });
      
      // Store tokens
      localStorage.setItem('access_token', authResponse.access_token);
      localStorage.setItem('refresh_token', authResponse.refresh_token);
      
      // Set user
      const userObj: User = {
        id: authResponse.id,
        email: authResponse.email,
        username: authResponse.username,
        full_name: authResponse.full_name,
        phone: authResponse.phone,
        company: authResponse.company,
        bio: authResponse.bio,
        is_active: authResponse.is_active,
        is_superuser: authResponse.is_superuser,
        is_verified: authResponse.is_verified,
        role: authResponse.role,
        created_at: authResponse.created_at,
        updated_at: authResponse.updated_at,
        last_login: authResponse.last_login,
      };
      
      setUser(userObj);
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await apiClient.logout();
    } catch (error) {
      // Even if logout fails on server, clear local state
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  };

  const refreshToken = async () => {
    try {
      const refresh_token = localStorage.getItem('refresh_token');
      if (!refresh_token) {
        throw new Error('No refresh token available');
      }

      const tokens = await apiClient.refreshToken(refresh_token);
      
      localStorage.setItem('access_token', tokens.access_token);
      localStorage.setItem('refresh_token', tokens.refresh_token);
    } catch (error) {
      // Refresh failed, logout user
      await logout();
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    refreshToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
