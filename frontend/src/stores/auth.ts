import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User, LoginRequest } from '@/types';
import { apiClient } from '@/utils/api';

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const isAuthenticated = computed(() => user.value !== null);
  const isAdmin = computed(() => user.value?.role === 'admin');
  const currentUser = computed(() => user.value);

  // Actions
  async function login(credentials: LoginRequest): Promise<boolean> {
    isLoading.value = true;
    error.value = null;

    try {
      await apiClient.login(credentials);
      await fetchCurrentUser();
      return true;
    } catch (err: any) {
      error.value = err.response?.data?.detail || '登录失败，请检查用户名和密码';
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function logout(): Promise<void> {
    user.value = null;
    apiClient.logout();
  }

  async function fetchCurrentUser(): Promise<void> {
    if (!apiClient.isAuthenticated()) {
      return;
    }

    isLoading.value = true;
    error.value = null;

    try {
      const userData = await apiClient.getCurrentUser();
      user.value = userData;
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取用户信息失败';
      // If token is invalid, logout
      if (err.response?.status === 401) {
        await logout();
      }
    } finally {
      isLoading.value = false;
    }
  }

  // Initialize auth state on store creation
  async function initialize(): Promise<void> {
    if (apiClient.isAuthenticated()) {
      await fetchCurrentUser();
    }
  }

  function clearError(): void {
    error.value = null;
  }

  return {
    // State
    user,
    isLoading,
    error,

    // Getters
    isAuthenticated,
    isAdmin,
    currentUser,

    // Actions
    login,
    logout,
    fetchCurrentUser,
    initialize,
    clearError,
  };
});
