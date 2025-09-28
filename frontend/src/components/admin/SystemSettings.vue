<template>
  <div class="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8 lg:ml-72">
    <div class="space-y-8">
      <!-- Header -->
      <div>
        <h1 class="text-2xl font-bold text-gray-900">系统设置</h1>
        <p class="mt-2 text-sm text-gray-600">管理系统存储配置和其他设置</p>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="flex justify-center py-12">
        <div class="h-8 w-8 animate-spin rounded-full border-2 border-primary-600 border-t-transparent"></div>
      </div>

      <!-- Settings Form -->
      <div v-else class="bg-white shadow rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">存储配置</h3>
          <p class="text-sm text-gray-500">选择头像和文件的存储方式</p>
        </div>
        
        <div class="px-6 py-6 space-y-6">
          <!-- Storage Provider Selection -->
          <div>
            <label class="text-base font-medium text-gray-900">存储提供商</label>
            <p class="text-sm leading-5 text-gray-500">选择文件存储的后端服务</p>
            <fieldset class="mt-4">
              <div class="space-y-4">
                <div class="flex items-center">
                  <input
                    id="local"
                    v-model="settings.storage.provider"
                    name="provider"
                    type="radio"
                    value="local"
                    class="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300"
                  />
                  <label for="local" class="ml-3">
                    <span class="block text-sm font-medium text-gray-700">本地存储</span>
                    <span class="block text-sm text-gray-500">文件存储在服务器本地文件系统</span>
                  </label>
                </div>
                
                <div class="flex items-center">
                  <input
                    id="alist"
                    v-model="settings.storage.provider"
                    name="provider"
                    type="radio"
                    value="alist"
                    class="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300"
                  />
                  <label for="alist" class="ml-3">
                    <span class="block text-sm font-medium text-gray-700">Alist 存储</span>
                    <span class="block text-sm text-gray-500">文件存储到 Alist 网盘服务</span>
                  </label>
                </div>
              </div>
            </fieldset>
          </div>

          <!-- Local Storage Settings -->
          <div v-show="settings.storage.provider === 'local'" class="space-y-4">
            <h4 class="text-lg font-medium text-gray-900">本地存储设置</h4>
            
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label class="block text-sm font-medium text-gray-700">上传路径</label>
                <input
                  v-model="settings.storage.local.upload_path"
                  type="text"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  placeholder="uploads/avatars"
                />
                <p class="mt-2 text-sm text-gray-500">相对于后端根目录的存储路径</p>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">访问基础URL</label>
                <input
                  v-model="settings.storage.local.base_url"
                  type="text"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  placeholder="/static/avatars"
                />
                <p class="mt-2 text-sm text-gray-500">用于生成文件访问链接的URL前缀</p>
              </div>
            </div>
          </div>

          <!-- Alist Storage Settings -->
          <div v-show="settings.storage.provider === 'alist'" class="space-y-4">
            <div class="flex items-center justify-between">
              <h4 class="text-lg font-medium text-gray-900">Alist 存储设置</h4>
              <button
                @click="testAlistConnection"
                :disabled="isTestingConnection || !settings.storage.alist.url || !settings.storage.alist.token"
                class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-if="isTestingConnection" class="mr-2">
                  <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </span>
                {{ isTestingConnection ? '测试中...' : '测试连接' }}
              </button>
            </div>
            
            <div class="grid grid-cols-1 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">Alist URL</label>
                <input
                  v-model="settings.storage.alist.url"
                  type="url"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  placeholder="https://your-alist-instance.com"
                />
                <p class="mt-2 text-sm text-gray-500">Alist 服务器的完整URL地址</p>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">访问Token</label>
                <input
                  v-model="settings.storage.alist.token"
                  type="password"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  placeholder="alist-your-secret-token"
                />
                <p class="mt-2 text-sm text-gray-500">用于访问 Alist API 的认证令牌</p>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">上传目录</label>
                <input
                  v-model="settings.storage.alist.upload_path"
                  type="text"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  placeholder="/_imageStore"
                />
                <p class="mt-2 text-sm text-gray-500">在 Alist 中存储文件的目录路径</p>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">自定义访问URL (可选)</label>
                <input
                  v-model="settings.storage.alist.custom_url"
                  type="url"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                  placeholder="留空使用默认URL"
                />
                <p class="mt-2 text-sm text-gray-500">自定义文件访问URL，留空则使用 Alist URL</p>
              </div>
            </div>
            
            <!-- Connection Test Result -->
            <div v-if="connectionTestResult" class="mt-4">
              <div 
                :class="[
                  'rounded-md p-4',
                  connectionTestResult.success 
                    ? 'bg-green-50 border border-green-200' 
                    : 'bg-red-50 border border-red-200'
                ]"
              >
                <div class="flex">
                  <div class="flex-shrink-0">
                    <CheckCircleIcon 
                      v-if="connectionTestResult.success" 
                      class="h-5 w-5 text-green-400" 
                    />
                    <XCircleIcon 
                      v-else 
                      class="h-5 w-5 text-red-400" 
                    />
                  </div>
                  <div class="ml-3">
                    <p 
                      :class="[
                        'text-sm font-medium',
                        connectionTestResult.success ? 'text-green-800' : 'text-red-800'
                      ]"
                    >
                      {{ connectionTestResult.message }}
                    </p>
                    <div v-if="connectionTestResult.success && connectionTestResult.user_info" class="mt-2 text-sm text-green-700">
                      <p>用户信息: {{ connectionTestResult.user_info.username || 'N/A' }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Save Button -->
          <div class="pt-6 border-t border-gray-200">
            <button
              @click="saveSettings"
              :disabled="isSaving"
              class="inline-flex justify-center items-center px-6 py-3 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="isSaving" class="mr-2">
                <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </span>
              {{ isSaving ? '保存中...' : '保存设置' }}
            </button>
          </div>
        </div>
      </div>
    </div>

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
import { ref, onMounted } from 'vue';
import { CheckCircleIcon, XCircleIcon } from '@heroicons/vue/24/outline';
import { useAuthStore } from '@/stores/auth';
import { apiClient } from '@/utils/api';

const authStore = useAuthStore();

// State
const isLoading = ref(true);
const isSaving = ref(false);
const isTestingConnection = ref(false);
const message = ref('');
const messageType = ref<'success' | 'error'>('success');
const connectionTestResult = ref<any>(null);

const settings = ref({
  storage: {
    provider: 'local',
    local: {
      upload_path: 'uploads/avatars',
      base_url: '/static/avatars'
    },
    alist: {
      url: '',
      token: '',
      upload_path: '/_imageStore',
      custom_url: ''
    }
  }
});

// Methods
async function loadSettings() {
  try {
    const data = await apiClient.getSystemSettings();
    settings.value = data;
  } catch (error) {
    console.error('Failed to load settings:', error);
    showMessage('加载设置失败', 'error');
  } finally {
    isLoading.value = false;
  }
}

async function saveSettings() {
  if (isSaving.value) return;
  
  isSaving.value = true;
  try {
    await apiClient.updateSystemSettings(settings.value);
    showMessage('设置保存成功', 'success');
    connectionTestResult.value = null; // Clear test result
  } catch (error: any) {
    console.error('Failed to save settings:', error);
    const errorMessage = error.response?.data?.detail || '保存设置失败';
    showMessage(errorMessage, 'error');
  } finally {
    isSaving.value = false;
  }
}

async function testAlistConnection() {
  if (isTestingConnection.value) return;
  
  isTestingConnection.value = true;
  connectionTestResult.value = null;
  
  try {
    const result = await apiClient.testAlistConnection(settings.value.storage.alist);
    connectionTestResult.value = result;
  } catch (error) {
    console.error('Failed to test connection:', error);
    connectionTestResult.value = {
      success: false,
      message: '测试连接时发生错误'
    };
  } finally {
    isTestingConnection.value = false;
  }
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
  await authStore.initialize();
  
  if (!authStore.isAuthenticated) {
    window.location.href = '/login';
    return;
  }
  
  if (!authStore.isAdmin) {
    window.location.href = '/dashboard/my-schedule';
    return;
  }
  
  await loadSettings();
});
</script>
