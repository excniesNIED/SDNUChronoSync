import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User } from '@/types';
import { apiClient } from '@/utils/api';

export const useTeamStore = defineStore('team', () => {
  // State
  const users = ref<User[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const lastFetchTime = ref<Date | null>(null);

  // Cache duration in milliseconds (5 minutes)
  const CACHE_DURATION = 5 * 60 * 1000;

  // Getters
  const userList = computed(() => users.value);
  const userMap = computed(() => {
    const map = new Map<number, User>();
    users.value.forEach(user => {
      map.set(user.id, user);
    });
    return map;
  });

  const getUserById = computed(() => {
    return (id: number): User | undefined => userMap.value.get(id);
  });

  const usersByClass = computed(() => {
    const groups = new Map<string, User[]>();
    users.value.forEach(user => {
      if (!groups.has(user.class_name)) {
        groups.set(user.class_name, []);
      }
      groups.get(user.class_name)!.push(user);
    });
    return groups;
  });

  const usersByGrade = computed(() => {
    const groups = new Map<string, User[]>();
    users.value.forEach(user => {
      if (!groups.has(user.grade)) {
        groups.set(user.grade, []);
      }
      groups.get(user.grade)!.push(user);
    });
    return groups;
  });

  const allClasses = computed(() => {
    const classes = new Set<string>();
    users.value.forEach(user => {
      classes.add(user.class_name);
    });
    return Array.from(classes).sort();
  });

  const allGrades = computed(() => {
    const grades = new Set<string>();
    users.value.forEach(user => {
      grades.add(user.grade);
    });
    return Array.from(grades).sort();
  });

  // Actions
  async function fetchUsers(forceRefresh = false): Promise<void> {
    // Check if we need to refresh based on cache duration
    if (!forceRefresh && lastFetchTime.value) {
      const timeSinceLastFetch = Date.now() - lastFetchTime.value.getTime();
      if (timeSinceLastFetch < CACHE_DURATION) {
        return;
      }
    }

    isLoading.value = true;
    error.value = null;

    try {
      const fetchedUsers = await apiClient.getAllUsers();
      users.value = fetchedUsers;
      lastFetchTime.value = new Date();
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取用户列表失败';
      console.error('Failed to fetch users:', err);
    } finally {
      isLoading.value = false;
    }
  }

  function searchUsers(query: string): User[] {
    if (!query.trim()) {
      return users.value;
    }

    const lowercaseQuery = query.toLowerCase();
    return users.value.filter(user => 
      user.full_name.toLowerCase().includes(lowercaseQuery) ||
      user.student_id.toLowerCase().includes(lowercaseQuery) ||
      user.class_name.toLowerCase().includes(lowercaseQuery) ||
      user.grade.toLowerCase().includes(lowercaseQuery)
    );
  }

  function filterUsers(filters: {
    class_name?: string;
    grade?: string;
    role?: 'user' | 'admin';
  }): User[] {
    return users.value.filter(user => {
      if (filters.class_name && user.class_name !== filters.class_name) {
        return false;
      }
      if (filters.grade && user.grade !== filters.grade) {
        return false;
      }
      if (filters.role && user.role !== filters.role) {
        return false;
      }
      return true;
    });
  }

  function clearError(): void {
    error.value = null;
  }

  function clearCache(): void {
    users.value = [];
    lastFetchTime.value = null;
  }

  return {
    // State
    users,
    isLoading,
    error,
    lastFetchTime,

    // Getters
    userList,
    userMap,
    getUserById,
    usersByClass,
    usersByGrade,
    allClasses,
    allGrades,

    // Actions
    fetchUsers,
    searchUsers,
    filterUsers,
    clearError,
    clearCache,
  };
});
