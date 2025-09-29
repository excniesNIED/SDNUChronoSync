<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h3 class="text-lg font-semibold text-gray-900">我的团队</h3>
      <button
        @click="refreshTeams"
        :disabled="loading"
        class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
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

    <!-- Loading State -->
    <div v-if="loading && teams.length === 0" class="text-center py-12">
      <svg class="animate-spin h-8 w-8 text-indigo-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <p class="mt-2 text-sm text-gray-500">加载中...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="teams.length === 0" class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">还没有加入任何团队</h3>
      <p class="mt-1 text-sm text-gray-500">创建一个新团队或使用团队代码加入现有团队</p>
    </div>

    <!-- Teams Grid -->
    <div v-else class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="team in teams"
        :key="team.id"
        class="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow duration-200"
      >
        <div class="p-6">
          <!-- Team Header -->
          <div class="flex items-start justify-between mb-4">
            <div class="flex-1 min-w-0">
              <h4 class="text-lg font-medium text-gray-900 truncate">
                {{ team.name }}
              </h4>
              <div class="flex items-center gap-2 mb-2">
                <span class="text-sm text-gray-500">
                  {{ team.members?.length || 0 }} 名成员
                </span>
                <!-- Members Avatar Preview -->
                <div class="flex -space-x-1" v-if="team.members && team.members.length > 0">
                  <UserAvatar 
                    v-for="(member, index) in team.members.slice(0, 3)"
                    :key="member.id"
                    :user="member" 
                    size="xs"
                    class="ring-2 ring-white"
                  />
                  <div 
                    v-if="team.members.length > 3"
                    class="w-6 h-6 rounded-full bg-gray-200 text-gray-600 text-xs font-medium flex items-center justify-center ring-2 ring-white"
                  >
                    +{{ team.members.length - 3 }}
                  </div>
                </div>
              </div>
              
              <!-- Creator Info -->
              <div class="flex items-center gap-2">
                <UserAvatar 
                  :user="team.creator" 
                  size="xs"
                />
                <span class="text-xs text-gray-500">
                  创建者: {{ team.creator?.full_name || '未知' }}
                </span>
              </div>
            </div>
            <div class="flex-shrink-0">
              <span
                v-if="isCreator(team)"
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
              >
                创建者
              </span>
              <span
                v-else
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
              >
                成员
              </span>
            </div>
          </div>

          <!-- Team Code -->
          <div class="mb-4 p-3 bg-gray-50 rounded-lg">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xs text-gray-500 mb-1">团队代码</p>
                <p class="text-sm font-mono font-semibold text-gray-900 tracking-wider">
                  {{ team.team_code }}
                </p>
              </div>
              <button
                @click="copyTeamCode(team.team_code)"
                class="text-gray-400 hover:text-gray-600 focus:outline-none"
                title="复制团队代码"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex flex-col sm:flex-row gap-2">
            <button
              @click="$emit('viewTeam', team.id)"
              class="flex-1 inline-flex items-center justify-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              查看课表
            </button>
            
            <div class="flex gap-2">
              <button
                v-if="canManage(team)"
                @click="openManageModal(team)"
                class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                title="管理团队"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
              
              <button
                v-if="isCreator(team)"
                @click="confirmDeleteTeam(team)"
                :disabled="deletingTeamId === team.id"
                class="inline-flex items-center px-3 py-2 border border-red-300 shadow-sm text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
                title="删除团队"
              >
                <svg v-if="deletingTeamId === team.id" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
              
              <button
                @click="confirmLeaveTeam(team)"
                :disabled="leavingTeamId === team.id"
                class="inline-flex items-center px-3 py-2 border border-red-300 shadow-sm text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
                title="退出团队"
              >
                <svg v-if="leavingTeamId === team.id" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Copy Success Toast -->
    <div
      v-if="showCopySuccess"
      class="fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-md shadow-lg z-50"
    >
      团队代码已复制到剪贴板
    </div>

    <!-- Team Editor Modal -->
    <TeamEditorModal
      v-if="showManageModal && selectedTeam"
      :team="selectedTeam"
      :user="user"
      @close="closeManageModal"
      @updated="handleTeamUpdated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useTeamStore } from '@/stores/team';
import { useAuthStore } from '@/stores/auth';
import TeamEditorModal from './TeamEditorModal.vue';
import UserAvatar from './UserAvatar.vue';
import type { Team, User } from '@/types';

// Props
interface Props {
  refreshTrigger?: number;
}

const props = withDefaults(defineProps<Props>(), {
  refreshTrigger: 0
});

// Stores
const teamStore = useTeamStore();
const authStore = useAuthStore();

// Reactive state
const leavingTeamId = ref<number | null>(null);
const deletingTeamId = ref<number | null>(null);
const showCopySuccess = ref(false);
const showManageModal = ref(false);
const selectedTeam = ref<Team | null>(null);

// Computed properties
const teams = computed(() => teamStore.teams);
const loading = computed(() => teamStore.loading);
const user = computed(() => authStore.user);

// Emit events
const emit = defineEmits<{
  viewTeam: [teamId: number];
  teamLeft: [teamId: number];
}>();

// Methods
const refreshTeams = async () => {
  await teamStore.fetchMyTeams();
};

const isCreator = (team: Team): boolean => {
  return team.creator_id === user.value?.id;
};

const canManage = (team: Team): boolean => {
  return user.value?.role === 'admin' || isCreator(team);
};

const copyTeamCode = async (teamCode: string) => {
  try {
    await navigator.clipboard.writeText(teamCode);
    showCopySuccess.value = true;
    setTimeout(() => {
      showCopySuccess.value = false;
    }, 2000);
  } catch (err) {
    console.error('Failed to copy team code:', err);
  }
};

const confirmLeaveTeam = (team: Team) => {
  const confirmed = confirm(`确定要退出团队"${team.name}"吗？`);
  if (confirmed) {
    leaveTeam(team);
  }
};

const leaveTeam = async (team: Team) => {
  try {
    leavingTeamId.value = team.id;
    await teamStore.leaveTeam(team.id);
    emit('teamLeft', team.id);
  } catch (error) {
    console.error('Failed to leave team:', error);
  } finally {
    leavingTeamId.value = null;
  }
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

const confirmDissolveTeam = (team: Team) => {
  const confirmed = confirm(`确定要解散团队"${team.name}"吗？此操作不可撤销！`);
  if (confirmed) {
    deleteTeam(team);
  }
};

const openTransferModal = (team: Team) => {
  // TODO: 实现转让功能
  alert(`转让功能即将开放，敬请期待！团队：${team.name}`);
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
    emit('teamLeft', team.id);
  } catch (error) {
    console.error('Failed to delete team:', error);
    alert('删除团队失败，请重试');
  } finally {
    deletingTeamId.value = null;
  }
};

// Lifecycle hooks
onMounted(() => {
  refreshTeams();
});

// Watch for refresh trigger changes
import { watch } from 'vue';
watch(() => props.refreshTrigger, () => {
  refreshTeams();
});
</script>
