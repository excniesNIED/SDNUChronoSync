<template>
  <div class="space-y-6">
    <!-- Action bar -->
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <div class="flex items-center gap-4">
          <!-- Search -->
          <div class="relative flex-1 max-w-md">
            <MagnifyingGlassIcon class="pointer-events-none absolute inset-y-0 left-0 h-full w-5 text-gray-400 pl-3" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索用户..."
              class="block w-full rounded-md border-0 py-1.5 pl-10 pr-3 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
            />
          </div>
          
          <!-- Role filter -->
          <select
            v-model="roleFilter"
            class="rounded-md border-0 py-1.5 px-3 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
          >
            <option value="">全部角色</option>
            <option value="user">用户</option>
            <option value="admin">管理员</option>
          </select>
        </div>
      </div>
      <div class="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
        <button
          @click="openCreateModal"
          class="block rounded-md bg-primary-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
        >
          添加用户
        </button>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="isLoading" class="flex justify-center py-12">
      <div class="h-8 w-8 animate-spin rounded-full border-2 border-primary-600 border-t-transparent"></div>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="rounded-md bg-red-50 p-4">
      <div class="flex">
        <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">{{ error }}</h3>
        </div>
      </div>
    </div>

    <!-- Users table -->
    <div v-else class="bg-white shadow-sm ring-1 ring-gray-900/5 rounded-lg">
      <table class="min-w-full divide-y divide-gray-300">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
              用户信息
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
              班级年级
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
              角色
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
              创建时间
            </th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">
              操作
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="user in filteredUsers" :key="user.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="flex-shrink-0 h-10 w-10">
                  <div class="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
                    <UserIcon class="h-6 w-6 text-primary-600" />
                  </div>
                </div>
                <div class="ml-4">
                  <div class="text-sm font-medium text-gray-900">{{ user.full_name }}</div>
                  <div class="text-sm text-gray-500">{{ user.student_id }}</div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              <div>{{ user.class_name }}</div>
              <div class="text-gray-500">{{ user.grade }}级</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                :class="[
                  user.role === 'admin'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-green-100 text-green-800',
                  'inline-flex px-2 py-1 text-xs font-semibold rounded-full'
                ]"
              >
                {{ user.role === 'admin' ? '管理员' : '用户' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatDate(user.created_at) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button
                @click="openEditModal(user)"
                class="text-primary-600 hover:text-primary-900 mr-3"
              >
                编辑
              </button>
              <button
                @click="confirmDelete(user)"
                :disabled="user.id === authStore.currentUser?.id"
                :class="[
                  user.id === authStore.currentUser?.id
                    ? 'text-gray-400 cursor-not-allowed'
                    : 'text-red-600 hover:text-red-900'
                ]"
              >
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty state -->
      <div v-if="filteredUsers.length === 0" class="text-center py-12">
        <UserGroupIcon class="mx-auto h-12 w-12 text-gray-400" />
        <h3 class="mt-2 text-sm font-semibold text-gray-900">没有找到用户</h3>
        <p class="mt-1 text-sm text-gray-500">尝试调整搜索条件或添加新用户。</p>
      </div>
    </div>

    <!-- User Modal -->
    <UserModal
      :is-open="isModalOpen"
      :user="selectedUser"
      @close="closeModal"
      @save="handleUserSave"
    />

    <!-- Delete Confirmation Modal -->
    <ConfirmDeleteModal
      :is-open="isDeleteModalOpen"
      :user="userToDelete"
      @close="closeDeleteModal"
      @confirm="handleUserDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import {
  MagnifyingGlassIcon,
  UserIcon,
  UserGroupIcon,
  ExclamationTriangleIcon,
} from '@heroicons/vue/24/outline';
import { apiClient } from '@/utils/api';
import { formatDisplayDate } from '@/utils/date';
import UserModal from './UserModal.vue';
import ConfirmDeleteModal from './ConfirmDeleteModal.vue';
import type { User } from '@/types';

const authStore = useAuthStore();

const users = ref<User[]>([]);
const isLoading = ref(false);
const error = ref<string | null>(null);
const searchQuery = ref('');
const roleFilter = ref('');

const isModalOpen = ref(false);
const selectedUser = ref<User | null>(null);

const isDeleteModalOpen = ref(false);
const userToDelete = ref<User | null>(null);

const filteredUsers = computed(() => {
  let filtered = users.value;

  // Search filter
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(user =>
      user.full_name.toLowerCase().includes(query) ||
      user.student_id.toLowerCase().includes(query) ||
      user.class_name.toLowerCase().includes(query)
    );
  }

  // Role filter
  if (roleFilter.value) {
    filtered = filtered.filter(user => user.role === roleFilter.value);
  }

  return filtered;
});

async function fetchUsers() {
  isLoading.value = true;
  error.value = null;

  try {
    users.value = await apiClient.getAllUsersAdmin();
  } catch (err: any) {
    error.value = err.response?.data?.detail || '获取用户列表失败';
    console.error('Failed to fetch users:', err);
  } finally {
    isLoading.value = false;
  }
}

function openCreateModal() {
  selectedUser.value = null;
  isModalOpen.value = true;
}

function openEditModal(user: User) {
  selectedUser.value = user;
  isModalOpen.value = true;
}

function closeModal() {
  isModalOpen.value = false;
  selectedUser.value = null;
}

async function handleUserSave(userData: any) {
  try {
    if (selectedUser.value) {
      // Update existing user
      const updatedUser = await apiClient.updateUser(selectedUser.value.id, userData);
      const index = users.value.findIndex(u => u.id === selectedUser.value!.id);
      if (index !== -1) {
        users.value[index] = updatedUser;
      }
    } else {
      // Create new user
      const newUser = await apiClient.createUser(userData);
      users.value.push(newUser);
    }
    closeModal();
  } catch (err: any) {
    console.error('Failed to save user:', err);
    // Error handling is done in the modal component
  }
}

function confirmDelete(user: User) {
  userToDelete.value = user;
  isDeleteModalOpen.value = true;
}

function closeDeleteModal() {
  isDeleteModalOpen.value = false;
  userToDelete.value = null;
}

async function handleUserDelete() {
  if (!userToDelete.value) return;

  try {
    await apiClient.deleteUser(userToDelete.value.id);
    users.value = users.value.filter(u => u.id !== userToDelete.value!.id);
    closeDeleteModal();
  } catch (err: any) {
    error.value = err.response?.data?.detail || '删除用户失败';
    console.error('Failed to delete user:', err);
  }
}

function formatDate(dateString: string): string {
  return formatDisplayDate(new Date(dateString));
}

onMounted(async () => {
  // Check authentication and admin role
  await authStore.initialize();
  
  if (!authStore.isAuthenticated) {
    window.location.href = '/login';
    return;
  }

  if (!authStore.isAdmin) {
    window.location.href = '/dashboard/my-schedule';
    return;
  }

  await fetchUsers();
});
</script>
