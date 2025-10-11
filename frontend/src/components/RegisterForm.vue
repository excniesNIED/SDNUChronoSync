<template>
  <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <div class="mx-auto flex items-center justify-center">
          <img src="/favicon.svg" alt="时序同笺" class="h-12 w-12" />
        </div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          注册时序同笺账户
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          或
          <a href="/login" class="font-medium text-primary-600 hover:text-primary-500">
            登录现有账户
          </a>
        </p>
      </div>

      <!-- Success Message -->
      <div v-if="successMessage" class="rounded-md bg-green-50 p-4">
        <div class="flex">
          <CheckCircleIcon class="h-5 w-5 text-green-400" />
          <div class="ml-3">
            <h3 class="text-sm font-medium text-green-800">
              {{ successMessage }}
            </h3>
          </div>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="rounded-md bg-red-50 p-4">
        <div class="flex">
          <ExclamationCircleIcon class="h-5 w-5 text-red-400" />
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">
              {{ errorMessage }}
            </h3>
          </div>
        </div>
      </div>

      <form @submit.prevent="handleSubmit" class="mt-8 space-y-6">
        <div class="space-y-4">
          <!-- Student ID -->
          <div>
            <label for="student_id" class="block text-sm font-medium text-gray-700">
              学号 <span class="text-red-500">*</span>
            </label>
            <input
              id="student_id"
              v-model="form.student_id"
              type="text"
              required
              :disabled="isLoading"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-50 disabled:text-gray-500"
              placeholder="请输入学号，如：202311001145"
            />
          </div>

          <!-- Full Name -->
          <div>
            <label for="full_name" class="block text-sm font-medium text-gray-700">
              姓名 <span class="text-red-500">*</span>
            </label>
            <input
              id="full_name"
              v-model="form.full_name"
              type="text"
              required
              :disabled="isLoading"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-50 disabled:text-gray-500"
              placeholder="请输入真实姓名"
            />
          </div>

          <!-- Class Name -->
          <div>
            <label for="class_name" class="block text-sm font-medium text-gray-700">
              班级 <span class="text-red-500">*</span>
            </label>
            <input
              id="class_name"
              v-model="form.class_name"
              type="text"
              required
              :disabled="isLoading"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-50 disabled:text-gray-500"
              placeholder="请输入班级，如：计工本2303"
            />
          </div>

          <!-- Grade -->
          <div>
            <label for="grade" class="block text-sm font-medium text-gray-700">
              年级 <span class="text-red-500">*</span>
            </label>
            <input
              id="grade"
              v-model="form.grade"
              type="text"
              required
              :disabled="isLoading"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-50 disabled:text-gray-500"
              placeholder="请输入年级，如：2023"
            />
          </div>

          <!-- Password -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">
              密码 <span class="text-red-500">*</span>
            </label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              :disabled="isLoading"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-50 disabled:text-gray-500"
              placeholder="请输入密码（至少6位）"
              minlength="6"
            />
          </div>

          <!-- Confirm Password -->
          <div>
            <label for="confirm_password" class="block text-sm font-medium text-gray-700">
              确认密码 <span class="text-red-500">*</span>
            </label>
            <input
              id="confirm_password"
              v-model="form.confirm_password"
              type="password"
              required
              :disabled="isLoading"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-50 disabled:text-gray-500"
              placeholder="请再次输入密码"
            />
            <div v-if="form.confirm_password && form.password !== form.confirm_password" class="mt-1 text-sm text-red-600">
              两次输入的密码不一致
            </div>
          </div>
        </div>

        <!-- Submit Button -->
        <div>
          <button
            type="submit"
            :disabled="isLoading || !isFormValid"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span class="absolute left-0 inset-y-0 flex items-center pl-3">
              <div v-if="isLoading" class="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
              <UserPlusIcon v-else class="h-5 w-5 text-primary-500 group-hover:text-primary-400" />
            </span>
            {{ isLoading ? '注册中...' : '创建账户' }}
          </button>
        </div>

        <!-- Login Link -->
        <div class="text-center">
          <span class="text-sm text-gray-600">
            已有账户？
            <a href="/login" class="font-medium text-primary-600 hover:text-primary-500">
              立即登录
            </a>
          </span>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { UserPlusIcon, CheckCircleIcon, ExclamationCircleIcon } from '@heroicons/vue/24/outline';
import { apiClient } from '@/utils/api';

const form = ref({
  student_id: '',
  full_name: '',
  class_name: '',
  grade: '',
  password: '',
  confirm_password: ''
});

const isLoading = ref(false);
const successMessage = ref('');
const errorMessage = ref('');

const isFormValid = computed(() => {
  return (
    form.value.student_id.trim() !== '' &&
    form.value.full_name.trim() !== '' &&
    form.value.class_name.trim() !== '' &&
    form.value.grade.trim() !== '' &&
    form.value.password.length >= 6 &&
    form.value.password === form.value.confirm_password
  );
});

async function handleSubmit() {
  if (!isFormValid.value) {
    errorMessage.value = '请填写所有必填字段并确保密码一致';
    return;
  }

  isLoading.value = true;
  successMessage.value = '';
  errorMessage.value = '';

  try {
    const response = await apiClient.register({
      student_id: form.value.student_id,
      full_name: form.value.full_name,
      class_name: form.value.class_name,
      grade: form.value.grade,
      password: form.value.password
    });

    successMessage.value = '注册成功！正在跳转到登录页面...';
    
    // 延迟跳转到登录页面
    setTimeout(() => {
      window.location.href = '/login?message=注册成功，请登录';
    }, 2000);

  } catch (error: any) {
    console.error('Registration failed:', error);
    
    if (error.response?.status === 400) {
      errorMessage.value = error.response.data.detail || '该学号已被注册，请使用其他学号';
    } else {
      errorMessage.value = error.response?.data?.detail || '注册失败，请稍后重试';
    }
  } finally {
    isLoading.value = false;
  }
}
</script>
