<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="handleOverlayClick">
    <div class="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <!-- Modal Header -->
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-gray-900">管理团队 - {{ team.name }}</h3>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 focus:outline-none"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Team Info Section -->
        <div class="mb-8">
          <h4 class="text-md font-medium text-gray-900 mb-4">团队信息</h4>
          <form @submit.prevent="updateTeamName" class="space-y-4">
            <div>
              <label for="teamName" class="block text-sm font-medium text-gray-700 mb-2">
                团队名称
              </label>
              <div class="flex gap-2">
                <input
                  id="teamName"
                  v-model="editedTeamName"
                  type="text"
                  required
                  class="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  :disabled="updatingName"
                />
                <button
                  type="submit"
                  :disabled="updatingName || editedTeamName === team.name"
                  class="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span v-if="updatingName">更新中...</span>
                  <span v-else>更新</span>
                </button>
              </div>
            </div>
          </form>

          <div class="mt-4 p-3 bg-gray-50 rounded-lg">
            <p class="text-sm text-gray-500 mb-1">团队代码</p>
            <div class="flex items-center justify-between">
              <p class="text-sm font-mono font-semibold text-gray-900 tracking-wider">
                {{ team.team_code }}
              </p>
              <button
                @click="copyTeamCode"
                class="text-gray-400 hover:text-gray-600 focus:outline-none"
                title="复制团队代码"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Members Management Section -->
        <div class="mb-8">
          <h4 class="text-md font-medium text-gray-900 mb-4">成员管理</h4>
          
          <!-- Add Member Form -->
          <form @submit.prevent="addMember" class="mb-6">
            <div class="flex gap-2">
              <input
                v-model="newMemberStudentId"
                type="text"
                placeholder="输入学号添加成员"
                required
                class="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                :disabled="addingMember"
              />
              <button
                type="submit"
                :disabled="addingMember || !newMemberStudentId.trim()"
                class="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-if="addingMember">添加中...</span>
                <span v-else>添加成员</span>
              </button>
            </div>
          </form>

          <!-- Members List -->
          <div class="space-y-2">
            <div
              v-for="member in team.members"
              :key="member.id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div class="flex items-center space-x-3">
                <div class="flex-shrink-0">
                  <UserAvatar 
                    :user="member" 
                    size="sm"
                  />
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ member.full_name }}</p>
                  <p class="text-xs text-gray-500">{{ member.student_id }} - {{ member.class_name }}</p>
                </div>
              </div>
              
              <div class="flex items-center space-x-2">
                <span
                  v-if="member.id === team.creator_id"
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
                
                <!-- Remove Member Button (only for non-creators and not self) -->
                <button
                  v-if="member.id !== team.creator_id && member.id !== user?.id"
                  @click="confirmRemoveMember(member)"
                  :disabled="removingMemberId === member.id"
                  class="text-red-400 hover:text-red-600 focus:outline-none disabled:opacity-50"
                  title="移除成员"
                >
                  <svg v-if="removingMemberId === member.id" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Danger Zone -->
        <div class="mb-6 p-4 border border-red-200 rounded-lg bg-red-50">
          <h4 class="text-md font-medium text-red-900 mb-2">危险操作</h4>
          <p class="text-sm text-red-700 mb-4">删除团队将永久删除所有团队数据，此操作不可撤销。</p>
          <button
            @click="confirmDeleteTeam"
            :disabled="deletingTeam"
            class="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="deletingTeam">删除中...</span>
            <span v-else>删除团队</span>
          </button>
        </div>

        <!-- Success/Error Messages -->
        <div v-if="successMessage" class="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
          <p class="text-sm text-green-800">{{ successMessage }}</p>
        </div>

        <div v-if="errorMessage" class="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <p class="text-sm text-red-800">{{ errorMessage }}</p>
        </div>

        <!-- Copy Success Toast -->
        <div
          v-if="showCopySuccess"
          class="fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-md shadow-lg z-50"
        >
          团队代码已复制到剪贴板
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useTeamStore } from '@/stores/team';
import { useAuthStore } from '@/stores/auth';
import UserAvatar from './UserAvatar.vue';
import type { Team, User } from '@/types';

// Props
interface Props {
  team: Team;
  user?: User | null;
}

const props = defineProps<Props>();

// Stores
const teamStore = useTeamStore();
const authStore = useAuthStore();

// Reactive state
const editedTeamName = ref('');
const newMemberStudentId = ref('');
const updatingName = ref(false);
const addingMember = ref(false);
const removingMemberId = ref<number | null>(null);
const deletingTeam = ref(false);
const successMessage = ref('');
const errorMessage = ref('');
const showCopySuccess = ref(false);

// Computed
const user = computed(() => props.user || authStore.user);

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

const updateTeamName = async () => {
  if (editedTeamName.value === props.team.name) return;
  
  try {
    updatingName.value = true;
    clearMessages();
    
    await teamStore.updateTeam(props.team.id, {
      name: editedTeamName.value
    });
    
    successMessage.value = '团队名称更新成功';
    emit('updated');
    
    setTimeout(() => {
      successMessage.value = '';
    }, 3000);
    
  } catch (err: any) {
    errorMessage.value = err.message || '更新团队名称失败';
  } finally {
    updatingName.value = false;
  }
};

const addMember = async () => {
  if (!newMemberStudentId.value.trim()) return;
  
  try {
    addingMember.value = true;
    clearMessages();
    
    await teamStore.addTeamMember(props.team.id, {
      student_id: newMemberStudentId.value.trim()
    });
    
    newMemberStudentId.value = '';
    successMessage.value = '成员添加成功';
    emit('updated');
    
    setTimeout(() => {
      successMessage.value = '';
    }, 3000);
    
  } catch (err: any) {
    errorMessage.value = err.message || '添加成员失败';
  } finally {
    addingMember.value = false;
  }
};

const confirmRemoveMember = (member: User) => {
  const confirmed = confirm(`确定要移除成员"${member.full_name}"吗？`);
  if (confirmed) {
    removeMember(member);
  }
};

const removeMember = async (member: User) => {
  try {
    removingMemberId.value = member.id;
    clearMessages();
    
    await teamStore.removeTeamMember(props.team.id, member.id);
    
    successMessage.value = `成功移除成员 ${member.full_name}`;
    emit('updated');
    
    setTimeout(() => {
      successMessage.value = '';
    }, 3000);
    
  } catch (err: any) {
    errorMessage.value = err.message || '移除成员失败';
  } finally {
    removingMemberId.value = null;
  }
};

const confirmDeleteTeam = () => {
  const confirmed = confirm(`确定要删除团队"${props.team.name}"吗？此操作不可撤销！`);
  if (confirmed) {
    deleteTeam();
  }
};

const deleteTeam = async () => {
  try {
    deletingTeam.value = true;
    clearMessages();
    
    await teamStore.deleteTeam(props.team.id);
    
    emit('updated');
    emit('close');
    
  } catch (err: any) {
    errorMessage.value = err.message || '删除团队失败';
  } finally {
    deletingTeam.value = false;
  }
};

const copyTeamCode = async () => {
  try {
    await navigator.clipboard.writeText(props.team.team_code);
    showCopySuccess.value = true;
    setTimeout(() => {
      showCopySuccess.value = false;
    }, 2000);
  } catch (err) {
    console.error('Failed to copy team code:', err);
  }
};

const clearMessages = () => {
  successMessage.value = '';
  errorMessage.value = '';
};

// Debug methods removed - only add when needed for troubleshooting

// Lifecycle
onMounted(() => {
  editedTeamName.value = props.team.name;
});
</script>
