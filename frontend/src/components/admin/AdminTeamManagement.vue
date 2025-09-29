<template>
  <div class="space-y-6">
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">总团队数</dt>
                <dd class="text-lg font-medium text-gray-900">{{ allTeams.length }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">总成员数</dt>
                <dd class="text-lg font-medium text-gray-900">{{ totalMembers }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 007.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721C7.456 2.41 9.71 2.25 12 2.25c2.291 0 4.545.16 6.75.47v1.516M7.73 9.728a6.726 6.726 0 002.748 1.35m8.272-6.842V4.5c0 2.108-.966 3.99-2.48 5.228m2.48-5.228a25.628 25.628 0 004.349.53m-4.349-.53v1.516l2.015.149c.913.07 1.848.143 2.793.22m-4.808-1.885c-.982-.143-1.954-.317-2.916-.52m0 0C10.456 2.41 8.71 2.25 6 2.25S1.544 2.41 0 2.721m3.75 1.515A6.726 6.726 0 016.498 5.59M6.498 5.59a6.726 6.726 0 01-1.35-2.748" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">平均成员数</dt>
                <dd class="text-lg font-medium text-gray-900">{{ averageMembers }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Search and Filter -->
    <div class="bg-white shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div class="flex-1 min-w-0">
            <div class="max-w-lg">
              <div class="relative rounded-md shadow-sm">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clip-rule="evenodd" />
                  </svg>
                </div>
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="搜索团队名称或创建者..."
                  class="focus:ring-indigo-500 focus:border-indigo-500 block w-full pl-10 sm:text-sm border-gray-300 rounded-md"
                />
              </div>
            </div>
          </div>
          <div class="mt-4 sm:mt-0 sm:ml-4">
            <button
              @click="refreshTeams"
              :disabled="loading"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              <svg 
                class="w-4 h-4 mr-2" 
                :class="{ 'animate-spin': loading }" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              刷新
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Teams Table -->
    <div class="bg-white shadow overflow-hidden sm:rounded-md">
      <div class="px-4 py-5 sm:px-6">
        <h3 class="text-lg leading-6 font-medium text-gray-900">团队列表</h3>
        <p class="mt-1 max-w-2xl text-sm text-gray-500">系统中所有团队的详细信息</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="px-4 py-5 sm:p-6 text-center">
        <div class="inline-flex items-center">
          <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          加载中...
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="px-4 py-5 sm:p-6 text-center">
        <div class="text-red-600">
          <svg class="mx-auto h-12 w-12 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">加载失败</h3>
          <p class="mt-1 text-sm text-gray-500">{{ error }}</p>
        </div>
      </div>

      <!-- Teams List -->
      <ul v-else-if="filteredTeams.length > 0" role="list" class="divide-y divide-gray-200">
        <li v-for="team in filteredTeams" :key="team.id" class="px-4 py-4 sm:px-6 hover:bg-gray-50">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                  <span class="text-sm font-medium text-indigo-800">{{ team.name.charAt(0) }}</span>
                </div>
              </div>
              <div class="ml-4">
                <div class="flex items-center">
                  <p class="text-sm font-medium text-gray-900">{{ team.name }}</p>
                  <span class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                    {{ team.team_code }}
                  </span>
                </div>
                <div class="mt-1 flex items-center text-sm text-gray-500">
                  <p>创建者: {{ team.creator?.full_name || '未知' }}</p>
                  <span class="mx-2">•</span>
                  <p>{{ team.members?.length || 0 }} 名成员</p>
                  <span class="mx-2">•</span>
                  <p>{{ formatDate(team.created_at) }}</p>
                </div>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <button
                @click="viewTeamDetails(team)"
                class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                查看
              </button>
              <button
                @click="openManageModal(team)"
                class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                管理
              </button>
              <button
                @click="confirmDeleteTeam(team)"
                :disabled="deletingTeamId === team.id"
                class="inline-flex items-center px-3 py-2 border border-red-300 shadow-sm text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
              >
                <svg v-if="deletingTeamId === team.id" class="animate-spin w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <svg v-else class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                删除
              </button>
            </div>
          </div>
        </li>
      </ul>

      <!-- Empty State -->
      <div v-else class="px-4 py-5 sm:p-6 text-center">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">没有找到团队</h3>
        <p class="mt-1 text-sm text-gray-500">{{ searchQuery ? '没有匹配的团队' : '系统中还没有任何团队' }}</p>
      </div>
    </div>

    <!-- Team Editor Modal -->
    <TeamEditorModal
      v-if="showManageModal && selectedTeam"
      :team="selectedTeam"
      :user="authStore.user"
      @close="closeManageModal"
      @updated="handleTeamUpdated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useTeamStore } from '@/stores/team';
import { useAuthStore } from '@/stores/auth';
import TeamEditorModal from '../TeamEditorModal.vue';
import type { Team } from '@/types';

// Stores
const teamStore = useTeamStore();
const authStore = useAuthStore();

// Reactive state
const searchQuery = ref('');
const showManageModal = ref(false);
const selectedTeam = ref<Team | null>(null);
const deletingTeamId = ref<number | null>(null);

// Computed properties
const allTeams = computed(() => teamStore.allTeams);
const loading = computed(() => teamStore.loading);
const error = computed(() => teamStore.error);

const filteredTeams = computed(() => {
  if (!searchQuery.value) {
    return allTeams.value;
  }
  
  const query = searchQuery.value.toLowerCase();
  return allTeams.value.filter(team => 
    team.name.toLowerCase().includes(query) ||
    team.team_code.toLowerCase().includes(query) ||
    team.creator?.full_name.toLowerCase().includes(query)
  );
});

const totalMembers = computed(() => {
  return allTeams.value.reduce((total, team) => total + (team.members?.length || 0), 0);
});

const averageMembers = computed(() => {
  if (allTeams.value.length === 0) return 0;
  return Math.round(totalMembers.value / allTeams.value.length * 10) / 10;
});

// Methods
const refreshTeams = async () => {
  try {
    await teamStore.fetchAllTeams();
  } catch (error) {
    console.error('Failed to fetch teams:', error);
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

const handleTeamUpdated = () => {
  refreshTeams();
  closeManageModal();
};

const confirmDeleteTeam = (team: Team) => {
  const confirmed = confirm(
    `确定要删除团队"${team.name}"吗？这将会删除团队的所有信息，此操作不可撤销！`
  );
  if (confirmed) {
    deleteTeam(team);
  }
};

const deleteTeam = async (team: Team) => {
  try {
    deletingTeamId.value = team.id;
    await teamStore.deleteTeam(team.id);
    await refreshTeams();
  } catch (error) {
    console.error('Failed to delete team:', error);
    alert('删除团队失败，请重试');
  } finally {
    deletingTeamId.value = null;
  }
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN');
};

// Lifecycle
onMounted(() => {
  refreshTeams();
});
</script>
