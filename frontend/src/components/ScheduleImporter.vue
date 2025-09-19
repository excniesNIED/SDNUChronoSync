<template>
  <TransitionRoot as="template" :show="isOpen">
    <Dialog as="div" class="relative z-50" @close="$emit('close')">
      <TransitionChild
        as="template"
        :show="isOpen"
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
            :show="isOpen"
            enter="ease-out duration-300"
            enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          >
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <div>
                <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-blue-100">
                  <CloudArrowDownIcon class="h-6 w-6 text-blue-600" aria-hidden="true" />
                </div>
                <div class="mt-3 text-center sm:mt-5">
                  <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">
                    从教务系统导入课表
                  </DialogTitle>
                  <div class="mt-2">
                    <p class="text-sm text-gray-500">
                      请输入您的教务系统账号密码，系统将自动导入您的课表信息。
                    </p>
                  </div>
                </div>
              </div>

              <form @submit.prevent="handleImport" class="mt-6">
                <div class="space-y-4">
                  <!-- Student ID -->
                  <div>
                    <label for="student_id" class="block text-sm font-medium leading-6 text-gray-900">
                      学号 <span class="text-red-500">*</span>
                    </label>
                    <input
                      id="student_id"
                      v-model="form.username"
                      type="text"
                      required
                      :disabled="isImporting"
                      class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6 disabled:bg-gray-50 disabled:text-gray-500"
                      placeholder="请输入教务系统学号"
                    />
                  </div>

                  <!-- Password -->
                  <div>
                    <label for="password" class="block text-sm font-medium leading-6 text-gray-900">
                      密码 <span class="text-red-500">*</span>
                    </label>
                    <input
                      id="password"
                      v-model="form.password"
                      type="password"
                      required
                      :disabled="isImporting"
                      class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6 disabled:bg-gray-50 disabled:text-gray-500"
                      placeholder="请输入教务系统密码"
                    />
                  </div>

                  <!-- Captcha -->
                  <div v-if="sessionData">
                    <label for="captcha" class="block text-sm font-medium leading-6 text-gray-900">
                      验证码 <span class="text-red-500">*</span>
                    </label>
                    <div class="mt-1 flex gap-3">
                      <input
                        id="captcha"
                        v-model="form.captcha"
                        type="text"
                        required
                        :disabled="isImporting"
                        class="block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6 disabled:bg-gray-50 disabled:text-gray-500"
                        placeholder="请输入验证码"
                      />
                      <div class="flex-shrink-0">
                        <img
                          :src="`data:image/png;base64,${sessionData.captcha_image}`"
                          alt="验证码"
                          class="h-10 w-20 border rounded cursor-pointer"
                          @click="refreshCaptcha"
                          title="点击刷新验证码"
                        />
                      </div>
                    </div>
                    <p class="mt-1 text-xs text-gray-500">点击验证码图片可刷新</p>
                  </div>

                  <!-- Important Notice -->
                  <div class="rounded-md bg-yellow-50 p-4">
                    <div class="flex">
                      <ExclamationTriangleIcon class="h-5 w-5 text-yellow-400" />
                      <div class="ml-3">
                        <h3 class="text-sm font-medium text-yellow-800">
                          重要提示
                        </h3>
                        <div class="mt-2 text-sm text-yellow-700">
                          <ul class="list-disc pl-5 space-y-1">
                            <li>您的密码仅用于一次性导入，不会被存储</li>
                            <li>导入将覆盖现有的课程数据</li>
                            <li>请确保网络连接正常</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Success Message -->
                <div v-if="successMessage" class="mt-4 rounded-md bg-green-50 p-4">
                  <div class="flex">
                    <CheckCircleIcon class="h-5 w-5 text-green-400" />
                    <div class="ml-3">
                      <h3 class="text-sm font-medium text-green-800">
                        {{ successMessage }}
                      </h3>
                    </div>
                  </div>
                </div>

                <!-- Error Message -->
                <div v-if="errorMessage" class="mt-4 rounded-md bg-red-50 p-4">
                  <div class="flex">
                    <ExclamationCircleIcon class="h-5 w-5 text-red-400" />
                    <div class="ml-3">
                      <h3 class="text-sm font-medium text-red-800">
                        {{ errorMessage }}
                      </h3>
                    </div>
                  </div>
                </div>

                <!-- Loading Progress -->
                <div v-if="isImporting" class="mt-4">
                  <div class="flex items-center">
                    <div class="flex-shrink-0">
                      <div class="h-5 w-5 animate-spin rounded-full border-2 border-blue-600 border-t-transparent"></div>
                    </div>
                    <div class="ml-3">
                      <p class="text-sm text-gray-600">{{ importStatus }}</p>
                    </div>
                  </div>
                  <div class="mt-2 w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-blue-600 h-2 rounded-full transition-all duration-300" :style="{ width: `${importProgress}%` }"></div>
                  </div>
                </div>

                <!-- Actions -->
                <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                  <button
                    type="submit"
                    :disabled="isImporting || !form.username || !form.password || !form.captcha || !sessionData"
                    class="inline-flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 disabled:opacity-50 disabled:cursor-not-allowed sm:col-start-2"
                  >
                    <CloudArrowDownIcon v-if="!isImporting" class="h-4 w-4 mr-2" />
                    {{ isImporting ? '导入中...' : '立即导入' }}
                  </button>
                  <button
                    type="button"
                    @click="$emit('close')"
                    :disabled="isImporting"
                    class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed sm:col-start-1 sm:mt-0"
                  >
                    {{ isImporting ? '导入中...' : '取消' }}
                  </button>
                </div>
              </form>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue';
import {
  CloudArrowDownIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
} from '@heroicons/vue/24/outline';
import { apiClient } from '@/utils/api';

interface Props {
  isOpen: boolean;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  close: [];
  success: [count: number];
}>();

const form = ref({
  username: '',
  password: '',
  captcha: '',
});

const isImporting = ref(false);
const importStatus = ref('');
const importProgress = ref(0);
const successMessage = ref('');
const errorMessage = ref('');
const sessionData = ref<{
  session_id: string;
  csrftoken: string;
  captcha_image: string;
} | null>(null);

async function handleImport() {
  if (!sessionData.value) {
    errorMessage.value = '会话数据缺失，请刷新验证码';
    return;
  }

  isImporting.value = true;
  importStatus.value = '正在验证登录信息...';
  importProgress.value = 20;
  successMessage.value = '';
  errorMessage.value = '';

  try {
    importStatus.value = '正在登录教务系统...';
    importProgress.value = 40;

    const response = await apiClient.importFromZFW({
      session_id: sessionData.value.session_id,
      username: form.value.username,
      password: form.value.password,
      captcha: form.value.captcha,
    });

    importStatus.value = '正在解析课表数据...';
    importProgress.value = 70;

    // 模拟解析时间
    await new Promise(resolve => setTimeout(resolve, 1000));

    importStatus.value = '正在保存课程信息...';
    importProgress.value = 90;

    // 再次模拟保存时间
    await new Promise(resolve => setTimeout(resolve, 500));

    importProgress.value = 100;

    if (response.success) {
      successMessage.value = response.message;
      
      // 延迟关闭并触发成功回调
      setTimeout(() => {
        emit('success', response.imported_count || 0);
        emit('close');
        resetForm();
      }, 2000);
    } else {
      errorMessage.value = response.message;
    }

  } catch (error: any) {
    console.error('Import failed:', error);
    errorMessage.value = error.response?.data?.detail || error.response?.data?.message || '导入失败，请检查网络连接或稍后重试';
  } finally {
    isImporting.value = false;
    importStatus.value = '';
    importProgress.value = 0;
  }
}

async function refreshCaptcha() {
  try {
    const response = await apiClient.getImportSession();
    sessionData.value = response;
    form.value.captcha = '';
  } catch (error) {
    console.error('Failed to refresh captcha:', error);
    errorMessage.value = '刷新验证码失败，请稍后重试';
  }
}

// 监听模态框打开事件，自动获取验证码
watch(() => props.isOpen, async (newValue) => {
  if (newValue && !sessionData.value) {
    await refreshCaptcha();
  }
});

function resetForm() {
  form.value = {
    username: '',
    password: '',
    captcha: '',
  };
  successMessage.value = '';
  errorMessage.value = '';
  sessionData.value = null;
}
</script>
