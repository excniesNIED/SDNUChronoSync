<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="handleOverlayClick">
    <div class="relative top-20 mx-auto p-5 border w-full max-w-md shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <!-- Modal Header -->
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-red-900">退出团队 - {{ team.name }}</h3>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 focus:outline-none"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Leave Form -->
        <div class="space-y-6">
          <div>
            <p class="text-sm text-gray-600 mb-4">
              您即将退出团队。退出后，您将失去对该团队的访问权限，需要重新加入才能访问。
            </p>
          </div>

          <!-- Warning -->
          <div class="rounded-md bg-yellow-50 p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-yellow-800">
                  确认退出
                </h3>
                <div class="mt-2 text-sm text-yellow-700">
                  <ul class="list-disc list-inside">
                    <li>您将失去对团队的访问权限</li>
                    <li>需要重新使用团队代码加入</li>
                    <li>您的个人课表不会受到影响</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <!-- Confirmation Input -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              确认退出，请输入团队名称: <strong>{{ team.name }}</strong>
            </label>
            <input
              v-model="confirmationText"
              type="text"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
              placeholder="请输入团队名称确认退出"
              :disabled="leaving"
            />
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="p-4 bg-red-50 border border-red-200 rounded-md">
            <p class="text-sm text-red-800">{{ errorMessage }}</p>
          </div>

          <!-- Action Buttons -->
          <div class="flex justify-end space-x-3">
            <button
              @click="$emit('close')"
              :disabled="leaving"
              class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              取消
            </button>
            <button
              @click="leaveTeam"
              :disabled="!canLeave || leaving"
              class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="leaving">退出中...</span>
              <span v-else>确认退出</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useTeamStore } from '@/stores/team';
import type { Team } from '@/types';

// Props
interface Props {
  team: Team;
}

const props = defineProps<Props>();

// Stores
const teamStore = useTeamStore();

// Reactive state
const confirmationText = ref('');
const leaving = ref(false);
const errorMessage = ref('');

// Computed properties
const canLeave = computed(() => {
  return confirmationText.value.trim() === props.team.name &&
         !leaving.value;
});

// Emit events
const emit = defineEmits<{
  close: [];
  left: [];
}>();

// Methods
const handleOverlayClick = (event: MouseEvent) => {
  if (event.target === event.currentTarget) {
    emit('close');
  }
};

const leaveTeam = async () => {
  if (!canLeave.value) return;
  
  try {
    leaving.value = true;
    errorMessage.value = '';
    
    await teamStore.leaveTeam(props.team.id);
    
    emit('left');
    emit('close');
    
  } catch (error: any) {
    console.error('Failed to leave team:', error);
    errorMessage.value = error.response?.data?.detail || '退出团队失败，请重试';
  } finally {
    leaving.value = false;
  }
};
</script>
