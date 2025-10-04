<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="handleOverlayClick">
    <div class="relative top-20 mx-auto p-5 border w-full max-w-6xl shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <!-- Modal Header -->
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-semibold text-gray-900">高级团队管理</h3>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 focus:outline-none"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Stats Cards for Created Teams -->
        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 mb-8">
          <div class="bg-white overflow-hidden shadow rounded-lg border">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg class="h-6 w-6 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">我创建的团队</dt>
                    <dd class="text-lg font-medium text-gray-900">{{ createdTeams.length }}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white overflow-hidden shadow rounded-lg border">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg class="h-6 w-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">团队总成员数</dt>
                    <dd class="text-lg font-medium text-gray-900">{{ totalMembersInCreatedTeams }}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white overflow-hidden shadow rounded-lg border">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg class="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 007.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721C7.456 2.41 9.71 2.25 12 2.25c2.291 0 4.545.16 6.75.47v1.516M7.73 9.728a6.726 6.726 0 002.748 1.35m8.272-6.842V4.5c0 2.108-.966 3.99-2.48 5.228m2.48-5.228a25.628 25.628 0 004.349.53m-4.349-.53v1.516l2.015.149c.913.07 1.848.143 2.793.22m-4.808-1.885c-.982-.143-1.954-.317-2.916-.52m0 0C10.456 2.41 8.71 2.25 6 2.25S1.544 2.41 0 2.721m3.75 1.515A6.726 6.726 0 016.498 5.59M6.498 5.59a6.726 6.726 0 01-1.35-2.748" />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">平均成员数</dt>
                    <dd class="text-lg font-medium text-gray-900">{{ averageMembersPerTeam }}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Search -->
        <div class="mb-6">
          <div class="max-w-lg w-full lg:max-w-xs">
            <label for="search" class="sr-only">搜索团队</label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
                </svg>
              </div>
              <input
                id="search"
                v-model="searchQuery"
                name="search"
                class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                placeholder="搜索团队名称或团队代码..."
                type="search"
              />
            </div>
          </div>
        </div>

        <!-- Teams Table -->
        <div class="bg-white shadow overflow-hidden rounded-md border max-h-96 overflow-y-auto">
          <!-- Loading State -->
          <div v-if="loading" class="px-4 py-8 text-center">
            <div class="inline-flex items-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              加载中...
            </div>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="px-4 py-8 text-center">
            <div class="text-red-600">
              <svg class="mx-auto h-12 w-12 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 class="mt-2 text-sm font-medium text-gray-900">加载失败</h3>
              <p class="mt-1 text-sm text-gray-500">{{ error }}</p>
            </div>
          </div>

          <!-- Teams List -->
          <ul v-else-if="filteredCreatedTeams.length > 0" role="list" class="divide-y divide-gray-200">
            <li v-for="team in filteredCreatedTeams" :key="team.id" class="px-4 py-4 sm:px-6 hover:bg-gray-50">
              <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div class="flex items-center min-w-0 flex-1">
                  <div class="flex-shrink-0">
                    <div class="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                      <span class="text-sm font-medium text-indigo-800">{{ team.name.charAt(0) }}</span>
                    </div>
                  </div>
                  <div class="ml-4 min-w-0 flex-1">
                    <div class="flex items-center flex-wrap gap-2">
                      <p class="text-sm font-medium text-gray-900 truncate">{{ team.name }}</p>
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 flex-shrink-0">
                        {{ team.team_code }}
                      </span>
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800 flex-shrink-0">
                        创建者
                      </span>
                    </div>
                    <div class="mt-1 flex items-center text-sm text-gray-500">
                      <p>{{ team.members?.length || 0 }} 名成员</p>
                      <span class="mx-2">•</span>
                      <p class="truncate">{{ formatDate(team.created_at) }}</p>
                    </div>
                  </div>
                </div>
                <div class="flex items-center gap-2 overflow-x-auto pb-2 sm:pb-0 flex-shrink-0">
                  <button
                    @click="viewTeamDetails(team)"
                    class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 whitespace-nowrap"
                    title="查看团队课表"
                  >
                    <svg class="w-4 h-4 sm:mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3a4 4 0 118 0v4m-4 1v0a8 8 0 00-7.864 9.746l.349 2.083A2 2 0 006.464 17h11.072a2 2 0 001.979-1.669l.349-2.083A8 8 0 0012 8v0z" />
                    </svg>
                    <span class="hidden sm:inline">课表</span>
                  </button>
                  <button
                    @click="openManageModal(team)"
                    class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 whitespace-nowrap"
                    title="管理团队"
                  >
                    <svg class="w-4 h-4 sm:mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    <span class="hidden sm:inline">管理</span>
                  </button>
                  <button
                    @click="openTransferModal(team)"
                    class="inline-flex items-center px-3 py-2 border border-orange-300 shadow-sm text-sm leading-4 font-medium rounded-md text-orange-700 bg-white hover:bg-orange-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 whitespace-nowrap"
                    title="转让团队"
                  >
                    <svg class="w-4 h-4 sm:mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                    </svg>
                    <span class="hidden sm:inline">转让</span>
                  </button>
                  <button
                    @click="openDissolveModal(team)"
                    class="inline-flex items-center px-3 py-2 border border-red-300 shadow-sm text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 whitespace-nowrap"
                    title="解散团队"
                  >
                    <svg class="w-4 h-4 sm:mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    <span class="hidden sm:inline">解散</span>
                  </button>
                </div>
              </div>
            </li>
          </ul>

          <!-- Empty State -->
          <div v-else class="px-4 py-8 text-center">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900">
              {{ searchQuery ? '没有找到匹配的团队' : '还没有创建任何团队' }}
            </h3>
            <p class="mt-1 text-sm text-gray-500">
              {{ searchQuery ? '尝试搜索其他关键词' : '创建您的第一个团队开始管理' }}
            </p>
          </div>
        </div>

        <!-- Success/Error Messages -->
        <div v-if="successMessage" class="mt-4 p-4 bg-green-50 border border-green-200 rounded-md">
          <p class="text-sm text-green-800">{{ successMessage }}</p>
        </div>

        <div v-if="errorMessage" class="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <p class="text-sm text-red-800">{{ errorMessage }}</p>
        </div>
      </div>
    </div>

    <!-- Team Editor Modal -->
    <TeamEditorModal
      v-if="showManageModal && selectedTeam"
      :team="selectedTeam"
      :user="user"
      @close="closeManageModal"
      @updated="handleTeamUpdated"
    />

    <!-- Transfer Modal -->
    <TransferTeamModal
      v-if="showTransferModal && selectedTeam"
      :team="selectedTeam"
      @close="closeTransferModal"
      @transferred="handleTeamTransferred"
    />

    <!-- Dissolve Modal -->
    <DissolveTeamModal
      v-if="showDissolveModal && selectedTeam"
      :team="selectedTeam"
      @close="closeDissolveModal"
      @dissolved="handleTeamDissolved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useTeamStore } from '@/stores/team';
import { useAuthStore } from '@/stores/auth';
import TeamEditorModal from './TeamEditorModal.vue';
import TransferTeamModal from './TransferTeamModal.vue';
import DissolveTeamModal from './DissolveTeamModal.vue';
import type { Team, User } from '@/types';

// Props
interface Props {
  user?: User | null;
}

const props = defineProps<Props>();

// Stores
const teamStore = useTeamStore();
const authStore = useAuthStore();

// Reactive state
const searchQuery = ref('');
const showManageModal = ref(false);
const showTransferModal = ref(false);
const showDissolveModal = ref(false);
const selectedTeam = ref<Team | null>(null);
// deletingTeamId 已移除，解散功能在模态框中处理
const successMessage = ref('');
const errorMessage = ref('');

// Computed properties
const user = computed(() => props.user || authStore.user);
const loading = computed(() => teamStore.loading);
const error = computed(() => teamStore.error);

const createdTeams = computed(() => {
  if (!user.value || !teamStore.teams) return [];
  return teamStore.teams.filter(team => team.creator_id === user.value?.id);
});

const filteredCreatedTeams = computed(() => {
  if (!searchQuery.value.trim()) {
    return createdTeams.value;
  }
  
  const query = searchQuery.value.toLowerCase().trim();
  return createdTeams.value.filter(team => 
    team.name.toLowerCase().includes(query) ||
    team.team_code.toLowerCase().includes(query)
  );
});

const totalMembersInCreatedTeams = computed(() => {
  return createdTeams.value.reduce((total, team) => total + (team.members?.length || 0), 0);
});

const averageMembersPerTeam = computed(() => {
  if (createdTeams.value.length === 0) return 0;
  return Math.round(totalMembersInCreatedTeams.value / createdTeams.value.length * 10) / 10;
});

// Emit events
const emit = defineEmits<{
  close: [];
  updated: [];
}>();

// Methods
const handleOverlayClick = (event: MouseEvent) => {
  if (event.target === event.currentTarget) {
    emit('close');
  }
};

const refreshTeams = async () => {
  try {
    await teamStore.fetchMyTeams();
  } catch (error) {
    console.error('Failed to fetch teams:', error);
    showError('获取团队列表失败，请重试');
  }
};

const viewTeamDetails = (team: Team) => {
  window.location.href = `/dashboard/team-view/${team.id}`;
};

const openManageModal = (team: Team) => {
  selectedTeam.value = team;
  showManageModal.value = true;
};

const closeManageModal = () => {
  showManageModal.value = false;
  selectedTeam.value = null;
};

const handleTeamUpdated = async () => {
  await refreshTeams();
  closeManageModal();
  emit('updated');
  showSuccess('团队信息更新成功');
};

const openTransferModal = (team: Team) => {
  selectedTeam.value = team;
  showTransferModal.value = true;
};

const closeTransferModal = () => {
  showTransferModal.value = false;
  selectedTeam.value = null;
};

const handleTeamTransferred = async () => {
  await refreshTeams();
  closeTransferModal();
  emit('updated');
  showSuccess('团队转让成功');
};

const openDissolveModal = (team: Team) => {
  selectedTeam.value = team;
  showDissolveModal.value = true;
};

const closeDissolveModal = () => {
  showDissolveModal.value = false;
  selectedTeam.value = null;
};

const handleTeamDissolved = async () => {
  await refreshTeams();
  closeDissolveModal();
  emit('updated');
  showSuccess('团队已解散');
};

// 解散团队功能已移至DissolveTeamModal中

import { formatDisplayDate } from '@/utils/date';

const formatDate = (dateString: string) => {
  try {
    return formatDisplayDate(dateString);
  } catch (error) {
    return '未知时间';
  }
};

const showSuccess = (message: string) => {
  successMessage.value = message;
  errorMessage.value = '';
  setTimeout(() => {
    successMessage.value = '';
  }, 5000);
};

const showError = (message: string) => {
  errorMessage.value = message;
  successMessage.value = '';
};

const clearMessages = () => {
  successMessage.value = '';
  errorMessage.value = '';
};

// Lifecycle
onMounted(() => {
  refreshTeams();
});
</script>
