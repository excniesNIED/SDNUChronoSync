<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="handleOverlayClick">
    <div class="relative top-20 mx-auto p-5 border w-full max-w-md shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <!-- Modal Header -->
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-gray-900">转让团队 - {{ team.name }}</h3>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 focus:outline-none"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Transfer Form -->
        <div class="space-y-6">
          <div>
            <p class="text-sm text-gray-600 mb-4">
              选择一个团队成员来转让团队的管理权。转让后，您将失去对该团队的管理权限。
            </p>
            
            <!-- Member Selection -->
            <div class="space-y-2">
              <label class="block text-sm font-medium text-gray-700">
                选择新的团队创建者
              </label>
              <select
                v-model="selectedMemberId"
                class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                :disabled="transferring"
              >
                <option value="">请选择团队成员...</option>
                <option
                  v-for="member in eligibleMembers"
                  :key="member.id"
                  :value="member.id"
                >
                  {{ member.full_name }} ({{ member.student_id }})
                </option>
              </select>
            </div>
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
                  注意事项
                </h3>
                <div class="mt-2 text-sm text-yellow-700">
                  <ul class="list-disc list-inside">
                    <li>转让后您将不再是团队创建者</li>
                    <li>新创建者将拥有团队的完全管理权限</li>
                    <li>此操作不可撤销</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <!-- Confirmation Input -->
          <div v-if="selectedMemberId">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              确认转让，请输入团队名称: <strong>{{ team.name }}</strong>
            </label>
            <input
              v-model="confirmationText"
              type="text"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
              placeholder="请输入团队名称确认转让"
              :disabled="transferring"
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
              :disabled="transferring"
              class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              取消
            </button>
            <button
              @click="transferTeam"
              :disabled="!canTransfer || transferring"
              class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-orange-600 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="transferring">转让中...</span>
              <span v-else>确认转让</span>
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
import { useAuthStore } from '@/stores/auth';
import type { Team } from '@/types';

// Props
interface Props {
  team: Team;
}

const props = defineProps<Props>();

// Stores
const teamStore = useTeamStore();
const authStore = useAuthStore();

// Reactive state
const selectedMemberId = ref<number | string>('');
const confirmationText = ref('');
const transferring = ref(false);
const errorMessage = ref('');

// Computed properties
const eligibleMembers = computed(() => {
  if (!props.team.members) return [];
  // 排除当前创建者
  return props.team.members.filter(member => member.id !== props.team.creator_id);
});

const canTransfer = computed(() => {
  return selectedMemberId.value && 
         confirmationText.value.trim() === props.team.name &&
         !transferring.value;
});

// Emit events
const emit = defineEmits<{
  close: [];
  transferred: [];
}>();

// Methods
const handleOverlayClick = (event: MouseEvent) => {
  if (event.target === event.currentTarget) {
    emit('close');
  }
};

const transferTeam = async () => {
  if (!canTransfer.value) return;
  
  try {
    transferring.value = true;
    errorMessage.value = '';
    
    // 调用团队转让API
    await teamStore.transferTeam(props.team.id, Number(selectedMemberId.value));
    
    emit('transferred');
    emit('close');
    
  } catch (error: any) {
    console.error('Failed to transfer team:', error);
    errorMessage.value = error.response?.data?.detail || '转让团队失败，请重试';
  } finally {
    transferring.value = false;
  }
};
</script>
