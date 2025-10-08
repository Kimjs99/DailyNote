'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  register: (email: string, password: string, name: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  api: ReturnType<typeof axios.create>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState<string | null>(
    typeof window !== 'undefined' ? localStorage.getItem('token') : null
  );

  // API 기본 설정
  const api = axios.create({
    baseURL: 'http://localhost:5001/api',
    timeout: 10000, // 10초 타임아웃
    headers: {
      'Content-Type': 'application/json',
    },
    withCredentials: true,
  });

  // 요청 인터셉터 - 토큰 자동 추가
  api.interceptors.request.use(
    (config) => {
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // 응답 인터셉터 - 토큰 만료 처리
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      console.error('API Error:', error);
      
      if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
        console.error('서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.');
      }
      
      if (error.response?.status === 401) {
        logout();
      }
      return Promise.reject(error);
    }
  );

  // 사용자 정보 로드
  const loadUser = useCallback(async () => {
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      console.log('Attempting to load user with token:', token);
      console.log('API base URL:', api.defaults.baseURL);
      
      // 먼저 서버 연결 테스트
      try {
        const testResponse = await fetch('http://localhost:5001/api/auth/me', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        console.log('Direct fetch test response:', testResponse.status);
      } catch (fetchError) {
        console.error('Direct fetch test failed:', fetchError);
      }
      
      const response = await api.get('/auth/me');
      console.log('User loaded successfully:', response.data);
      setUser(response.data.user);
    } catch (error) {
      console.error('Failed to load user:', error);
      console.error('Error details:', {
        message: error.message,
        code: error.code,
        response: error.response?.data,
        status: error.response?.status
      });
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
      }
      setToken(null);
    } finally {
      setLoading(false);
    }
  }, [token, api]);

  // 회원가입
  const register = async (email: string, password: string, name: string) => {
    try {
      const response = await api.post('/auth/register', {
        email,
        password,
        name,
      });

      const { token: newToken, user: newUser } = response.data;
      setToken(newToken);
      setUser(newUser);
      if (typeof window !== 'undefined') {
        localStorage.setItem('token', newToken);
      }
      return { success: true };
    } catch (error: unknown) {
      let errorMessage = 'Registration failed';
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { data?: { error?: string } } };
        errorMessage = axiosError.response?.data?.error || 'Registration failed';
      }
      return {
        success: false,
        error: errorMessage,
      };
    }
  };

  // 로그인
  const login = async (email: string, password: string) => {
    try {
      console.log('Attempting login with email:', email);
      const response = await api.post('/auth/login', {
        email,
        password,
      });

      console.log('Login response:', response.data);
      const { token: newToken, user: newUser } = response.data;
      setToken(newToken);
      setUser(newUser);
      if (typeof window !== 'undefined') {
        localStorage.setItem('token', newToken);
      }
      return { success: true };
    } catch (error: unknown) {
      console.error('Login error:', error);
      let errorMessage = 'Login failed';
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { data?: { error?: string } } };
        errorMessage = axiosError.response?.data?.error || 'Login failed';
        console.error('Login error details:', {
          status: axiosError.response?.status,
          data: axiosError.response?.data
        });
      }
      return {
        success: false,
        error: errorMessage,
      };
    }
  };

  // 로그아웃
  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setToken(null);
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
      }
    }
  };

  // 컴포넌트 마운트 시 사용자 정보 로드
  useEffect(() => {
    loadUser();
  }, [token, loadUser]);

  const value = {
    user,
    loading,
    register,
    login,
    logout,
    api,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
