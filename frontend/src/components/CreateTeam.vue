<template>
  <div class="bg-white rounded-lg shadow p-6">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">创建团队</h3>
    
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label for="teamName" class="block text-sm font-medium text-gray-700 mb-2">
          团队名称
        </label>
        <input
          id="teamName"
          v-model="teamName"
          type="text"
          required
          placeholder="请输入团队名称"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          :disabled="loading"
        />
      </div>
      
      <div class="flex justify-end">
        <button
          type="submit"
          :disabled="loading || !teamName.trim()"
          class="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="loading" class="flex items-center">
            <svg class="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            创建中...
          </span>
          <span v-else>创建团队</span>
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
          <p class="text-sm text-green-800">团队创建成功！</p>
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
import { ref } from 'vue';
import { useTeamStore } from '@/stores/team';

// Reactive state
const teamName = ref('');
const loading = ref(false);
const showSuccess = ref(false);
const error = ref<string | null>(null);

// Store
const teamStore = useTeamStore();

// Emit events
const emit = defineEmits<{
  teamCreated: [team: any];
}>();

// Methods
const handleSubmit = async () => {
  if (!teamName.value.trim()) return;
  
  try {
    loading.value = true;
    error.value = null;
    showSuccess.value = false;
    
    const newTeam = await teamStore.createTeam({
      name: teamName.value.trim()
    });
    
    // Show success message
    showSuccess.value = true;
    teamName.value = '';
    
    // Emit event for parent component
    emit('teamCreated', newTeam);
    
    // Hide success message after 3 seconds
    setTimeout(() => {
      showSuccess.value = false;
    }, 3000);
    
  } catch (err: any) {
    error.value = err.message || '创建团队失败，请重试';
  } finally {
    loading.value = false;
  }
};
</script>
