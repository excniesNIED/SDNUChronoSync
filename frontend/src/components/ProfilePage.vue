<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Main Content (removed separate header) -->

    <main class="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8 lg:ml-72">
      <div class="space-y-8">
        <!-- Profile Card -->
        <div class="bg-white shadow rounded-lg">
          <div class="px-6 py-8">
            <div class="flex items-center space-x-6">
              <!-- Avatar Section -->
              <div class="flex-shrink-0">
                <div class="relative">
                  <img
                    :src="profileData.avatar_url || defaultAvatar"
                    :alt="`${profileData.full_name}的头像`"
                    class="h-24 w-24 rounded-full object-cover border-4 border-gray-200"
                  />
                  <button
                    @click="showAvatarModal = true"
                    class="absolute bottom-0 right-0 bg-primary-600 text-white rounded-full p-2 shadow-lg hover:bg-primary-700 transition-colors"
                  >
                    <CameraIcon class="h-4 w-4" />
                  </button>
                </div>
              </div>

              <!-- Profile Info -->
              <div class="flex-1">
                <h2 class="text-2xl font-bold text-gray-900">{{ profileData.full_name }}</h2>
                <p class="text-gray-600">学号: {{ profileData.student_id }}</p>
                <p class="text-gray-600">班级: {{ profileData.class_name }}</p>
                <p class="text-gray-600">年级: {{ profileData.grade }}</p>
                <div class="mt-2">
                  <span :class="[
                    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                    profileData.role === 'admin' 
                      ? 'bg-purple-100 text-purple-800' 
                      : 'bg-green-100 text-green-800'
                  ]">
                    {{ profileData.role === 'admin' ? '管理员' : '普通用户' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Settings Sections -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Account Settings -->
          <div class="bg-white shadow rounded-lg">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-lg font-medium text-gray-900">账户设置</h3>
            </div>
            <div class="px-6 py-6 space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">姓名</label>
                <input
                  v-model="editData.full_name"
                  type="text"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">班级</label>
                <input
                  v-model="editData.class_name"
                  type="text"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">年级</label>
                <input
                  v-model="editData.grade"
                  type="text"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              <div class="pt-4">
                <button
                  @click="updateProfile"
                  :disabled="isUpdating"
                  class="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span v-if="isUpdating" class="mr-2">
                    <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  </span>
                  {{ isUpdating ? '保存中...' : '保存更改' }}
                </button>
              </div>
            </div>
          </div>

          <!-- Security Settings -->
          <div class="bg-white shadow rounded-lg">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-lg font-medium text-gray-900">安全设置</h3>
            </div>
            <div class="px-6 py-6 space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">当前密码</label>
                <input
                  v-model="passwordData.currentPassword"
                  type="password"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  placeholder="请输入当前密码"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">新密码</label>
                <input
                  v-model="passwordData.newPassword"
                  type="password"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  placeholder="请输入新密码"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">确认新密码</label>
                <input
                  v-model="passwordData.confirmPassword"
                  type="password"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  placeholder="请再次输入新密码"
                />
              </div>
              <div class="pt-4">
                <button
                  @click="changePassword"
                  :disabled="isChangingPassword || !isPasswordFormValid"
                  class="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span v-if="isChangingPassword" class="mr-2">
                    <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  </span>
                  {{ isChangingPassword ? '修改中...' : '修改密码' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Statistics Card -->
        <div class="bg-white shadow rounded-lg">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">账户统计</h3>
          </div>
          <div class="px-6 py-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div class="text-center">
                <div class="text-2xl font-bold text-primary-600">{{ statistics.scheduleCount }}</div>
                <div class="text-sm text-gray-500">我的课表</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-green-600">{{ statistics.eventCount }}</div>
                <div class="text-sm text-gray-500">总课程数</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-blue-600">{{ formatJoinDate(profileData.created_at) }}</div>
                <div class="text-sm text-gray-500">注册时间</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Avatar Modal -->
    <TransitionRoot as="template" :show="showAvatarModal">
      <Dialog as="div" class="relative z-50" @close="showAvatarModal = false">
        <TransitionChild
          as="template"
          enter="ease-out duration-300"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="ease-in duration-200"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </TransitionChild>

        <div class="fixed inset-0 z-10 overflow-y-auto">
          <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <TransitionChild
              as="template"
              enter="ease-out duration-300"
              enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enter-to="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leave-from="opacity-100 translate-y-0 sm:scale-100"
              leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                <div>
                  <div class="text-center">
                    <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">
                      更改头像
                    </DialogTitle>
                    <div class="mt-4 space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">头像链接</label>
                        <input
                          v-model="avatarUrl"
                          type="url"
                          class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                          placeholder="https://example.com/avatar.jpg"
                        />
                      </div>
                      
                      <div class="text-center text-gray-500">或</div>
                      
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">上传头像</label>
                        <div class="flex items-center justify-center">
                          <label class="cursor-pointer bg-white py-2 px-3 border border-gray-300 rounded-md shadow-sm text-sm leading-4 font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
                            <span>选择文件</span>
                            <input
                              type="file"
                              class="sr-only"
                              accept="image/*"
                              @change="handleFileUpload"
                            />
                          </label>
                        </div>
                        <p class="mt-2 text-xs text-gray-500">支持 JPG, PNG, GIF 格式，最大 2MB</p>
                      </div>

                      <!-- Preview -->
                      <div v-if="avatarUrl" class="text-center">
                        <img
                          :src="avatarUrl"
                          alt="头像预览"
                          class="h-20 w-20 rounded-full object-cover mx-auto border-2 border-gray-200"
                          @error="avatarUrl = ''"
                        />
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                  <button
                    type="button"
                    @click="updateAvatar"
                    :disabled="!avatarUrl || isUpdatingAvatar"
                    class="inline-flex w-full justify-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600 disabled:opacity-50 disabled:cursor-not-allowed sm:col-start-2"
                  >
                    {{ isUpdatingAvatar ? '保存中...' : '保存' }}
                  </button>
                  <button
                    type="button"
                    @click="showAvatarModal = false"
                    class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0"
                  >
                    取消
                  </button>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>

    <!-- Success/Error Messages -->
    <div
      v-if="message"
      :class="[
        'fixed top-4 right-4 px-4 py-2 rounded-md shadow-lg z-50 transition-all duration-300',
        messageType === 'success' 
          ? 'bg-green-100 text-green-800 border border-green-200' 
          : 'bg-red-100 text-red-800 border border-red-200'
      ]"
    >
      {{ message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue';
import { ArrowLeftIcon, CameraIcon } from '@heroicons/vue/24/outline';
import { useAuthStore } from '@/stores/auth';
import { useScheduleStore } from '@/stores/schedule';
import { apiClient } from '@/utils/api';
import type { User } from '@/types';

const authStore = useAuthStore();
const scheduleStore = useScheduleStore();

// State
const profileData = ref<User>({
  id: 0,
  student_id: '',
  full_name: '',
  class_name: '',
  grade: '',
  role: 'user',
  created_at: '',
  avatar_url: ''
} as any);

const editData = ref({
  full_name: '',
  class_name: '',
  grade: ''
});

const passwordData = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});

const statistics = ref({
  scheduleCount: 0,
  eventCount: 0
});

const showAvatarModal = ref(false);
const avatarUrl = ref('');
const isUpdating = ref(false);
const isChangingPassword = ref(false);
const isUpdatingAvatar = ref(false);
const message = ref('');
const messageType = ref<'success' | 'error'>('success');

// Computed
const defaultAvatar = computed(() => {
  const name = profileData.value.full_name;
  if (!name) return '/default-avatar.png';
  
  // 使用名字生成默认头像（这里使用一个简单的API）
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&size=200&background=6366f1&color=ffffff`;
});

const isPasswordFormValid = computed(() => {
  return (
    passwordData.value.currentPassword &&
    passwordData.value.newPassword &&
    passwordData.value.confirmPassword &&
    passwordData.value.newPassword === passwordData.value.confirmPassword &&
    passwordData.value.newPassword.length >= 6
  );
});

// Methods
async function loadProfile() {
  try {
    await authStore.initialize();
    if (authStore.user) {
      profileData.value = { ...authStore.user };
      editData.value = {
        full_name: authStore.user.full_name,
        class_name: authStore.user.class_name,
        grade: authStore.user.grade
      };
    }
  } catch (error) {
    console.error('Failed to load profile:', error);
  }
}

async function loadStatistics() {
  try {
    const stats = await apiClient.getProfileStatistics();
    statistics.value.scheduleCount = stats.schedule_count;
    statistics.value.eventCount = stats.event_count;
  } catch (error) {
    console.error('Failed to load statistics:', error);
  }
}

async function updateProfile() {
  if (isUpdating.value) return;
  
  isUpdating.value = true;
  try {
    const updatedProfile = await apiClient.updateProfile(editData.value);
    
    profileData.value.full_name = updatedProfile.full_name;
    profileData.value.class_name = updatedProfile.class_name;
    profileData.value.grade = updatedProfile.grade;
    
    // 更新auth store中的用户信息
    authStore.user = updatedProfile;
    
    showMessage('个人信息更新成功', 'success');
  } catch (error) {
    console.error('Failed to update profile:', error);
    showMessage('个人信息更新失败', 'error');
  } finally {
    isUpdating.value = false;
  }
}

async function changePassword() {
  if (isChangingPassword.value || !isPasswordFormValid.value) return;
  
  isChangingPassword.value = true;
  try {
    await apiClient.changePassword({
      current_password: passwordData.value.currentPassword,
      new_password: passwordData.value.newPassword
    });
    
    passwordData.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    };
    
    showMessage('密码修改成功', 'success');
  } catch (error) {
    console.error('Failed to change password:', error);
    showMessage('密码修改失败，请检查当前密码是否正确', 'error');
  } finally {
    isChangingPassword.value = false;
  }
}

async function updateAvatar() {
  if (isUpdatingAvatar.value || !avatarUrl.value) return;
  
  isUpdatingAvatar.value = true;
  try {
    const result = await apiClient.updateAvatar({ avatar_url: avatarUrl.value });
    
    profileData.value.avatar_url = result.avatar_url;
    showAvatarModal.value = false;
    avatarUrl.value = '';
    
    showMessage('头像更新成功', 'success');
  } catch (error) {
    console.error('Failed to update avatar:', error);
    showMessage('头像更新失败', 'error');
  } finally {
    isUpdatingAvatar.value = false;
  }
}

function handleFileUpload(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) return;
  
  // 检查文件大小（2MB）
  if (file.size > 2 * 1024 * 1024) {
    showMessage('文件大小不能超过 2MB', 'error');
    return;
  }
  
  // 检查文件类型
  if (!file.type.startsWith('image/')) {
    showMessage('请选择图片文件', 'error');
    return;
  }
  
  // 创建预览
  const reader = new FileReader();
  reader.onload = (e) => {
    avatarUrl.value = e.target?.result as string;
  };
  reader.readAsDataURL(file);
}

function formatJoinDate(dateString: string): string {
  if (!dateString) return '未知';
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN');
}

function showMessage(text: string, type: 'success' | 'error') {
  message.value = text;
  messageType.value = type;
  setTimeout(() => {
    message.value = '';
  }, 3000);
}

// Initialize
onMounted(async () => {
  await loadProfile();
  await loadStatistics();
});
</script>
