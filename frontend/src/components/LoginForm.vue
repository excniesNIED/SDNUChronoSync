<template>
  <form @submit.prevent="handleSubmit" class="mt-8 space-y-6">
    <div class="rounded-md shadow-sm space-y-4">
      <div>
        <label for="student_id" class="block text-sm font-medium text-gray-700 mb-1">
          学号或用户名
        </label>
        <input
          id="student_id"
          v-model="form.student_id"
          name="student_id"
          type="text"
          required
          class="relative block w-full rounded-md border-0 py-2 px-3 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:z-10 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
          placeholder="请输入学号或用户名"
        />
      </div>
      <div>
        <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
          密码
        </label>
        <input
          id="password"
          v-model="form.password"
          name="password"
          type="password"
          required
          class="relative block w-full rounded-md border-0 py-2 px-3 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:z-10 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
          placeholder="请输入密码"
        />
      </div>
    </div>

    <!-- Error message -->
    <div v-if="authStore.error" class="rounded-md bg-red-50 p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">
            {{ authStore.error }}
          </h3>
        </div>
      </div>
    </div>

    <div>
      <button
        type="submit"
        :disabled="authStore.isLoading"
        class="group relative flex w-full justify-center rounded-md bg-primary-600 py-2 px-3 text-sm font-semibold text-white hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        <span v-if="authStore.isLoading" class="absolute inset-y-0 left-0 flex items-center pl-3">
          <div class="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
        </span>
        {{ authStore.isLoading ? '登录中...' : '登录' }}
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline';

const authStore = useAuthStore();

const form = ref({
  student_id: '',
  password: '',
});

onMounted(() => {
  // Clear any previous errors
  authStore.clearError();
  
  // Simple check: if user has a valid token, redirect to dashboard
  // We don't call initialize here to avoid conflicts with dashboard auth check
  if (localStorage.getItem('access_token')) {
    window.location.href = '/dashboard/my-schedule';
  }
});

async function handleSubmit() {
  authStore.clearError();
  
  const success = await authStore.login({
    student_id: form.value.student_id,
    password: form.value.password,
  });

  if (success) {
    // Redirect to dashboard on successful login
    window.location.href = '/dashboard/my-schedule';
  }
}
</script>
