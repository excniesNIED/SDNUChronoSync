<template>
  <div class="bg-white rounded-lg shadow p-6">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">加入团队</h3>
    
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label for="teamCode" class="block text-sm font-medium text-gray-700 mb-2">
          团队代码
        </label>
        <input
          id="teamCode"
          v-model="teamCode"
          type="text"
          required
          placeholder="请输入8位团队代码"
          maxlength="8"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent uppercase tracking-wider"
          :disabled="loading"
          @input="teamCode = teamCode.toUpperCase()"
        />
        <p class="mt-1 text-xs text-gray-500">团队代码由8位字母和数字组成</p>
      </div>
      
      <div class="flex justify-end">
        <button
          type="submit"
          :disabled="loading || !isValidTeamCode"
          class="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="loading" class="flex items-center">
            <svg class="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            加入中...
          </span>
          <span v-else>加入团队</span>
        </button>
      </div>
    </form>
    
    <!-- Success Message -->
    <div v-if="showSuccess" class="mt-4 p-4 bg-green-50 border border-green-200 rounded-md">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-green-800">成功加入团队：{{ joinedTeamName }}</p>
        </div>
      </div>
    </div>
    
    <!-- Error Message -->
    <div v-if="error" class="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-800">{{ error }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useTeamStore } from '@/stores/team';
import type { Team } from '@/types';

// Reactive state
const teamCode = ref('');
const loading = ref(false);
const showSuccess = ref(false);
const joinedTeamName = ref('');
const error = ref<string | null>(null);

// Store
const teamStore = useTeamStore();

// Computed properties
const isValidTeamCode = computed(() => {
  const code = teamCode.value.trim();
  return code.length === 8 && /^[A-Z0-9]+$/.test(code);
});

// Emit events
const emit = defineEmits<{
  teamJoined: [team: Team];
}>();

// Methods
const handleSubmit = async () => {
  if (!isValidTeamCode.value) return;
  
  try {
    loading.value = true;
    error.value = null;
    showSuccess.value = false;
    
    const team = await teamStore.joinTeam({
      team_code: teamCode.value.trim()
    });
    
    // Show success message
    showSuccess.value = true;
    joinedTeamName.value = team.name;
    teamCode.value = '';
    
    // Emit event for parent component
    emit('teamJoined', team);
    
    // Hide success message after 3 seconds
    setTimeout(() => {
      showSuccess.value = false;
    }, 3000);
    
  } catch (err: any) {
    const errorMessage = err.message || '加入团队失败';
    if (errorMessage.includes('Invalid team code') || errorMessage.includes('团队代码')) {
      error.value = '团队代码无效，请检查后重试';
    } else {
      error.value = errorMessage;
    }
  } finally {
    loading.value = false;
  }
};
</script>
