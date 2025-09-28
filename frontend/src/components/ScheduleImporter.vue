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
                  <div>
                    <label for="captcha" class="block text-sm font-medium leading-6 text-gray-900">
                      验证码 <span class="text-red-500">*</span>
                    </label>
                    <div class="mt-1 flex gap-3">
                      <input
                        id="captcha"
                        v-model="form.captcha"
                        type="text"
                        required
                        :disabled="isImporting || !sessionData"
                        class="block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6 disabled:bg-gray-50 disabled:text-gray-500"
                        placeholder="请输入验证码"
                      />
                      <div class="flex-shrink-0 relative">
                        <!-- Loading state -->
                        <div v-if="isLoadingCaptcha" class="h-10 w-20 border rounded bg-gray-100 flex items-center justify-center">
                          <div class="h-4 w-4 animate-spin rounded-full border-2 border-blue-600 border-t-transparent"></div>
                        </div>
                        <!-- Captcha image -->
                        <img
                          v-else-if="sessionData?.captcha_image"
                          :src="`data:image/png;base64,${sessionData.captcha_image}`"
                          alt="验证码"
                          class="h-10 w-20 border rounded cursor-pointer hover:opacity-80 transition-opacity"
                          @click="refreshCaptcha"
                          title="点击刷新验证码"
                        />
                        <!-- Error state -->
                        <div v-else class="h-10 w-20 border rounded bg-red-50 flex items-center justify-center cursor-pointer hover:bg-red-100"
                             @click="refreshCaptcha"
                             title="点击重新加载验证码">
                          <span class="text-xs text-red-600">加载失败</span>
                        </div>
                      </div>
                    </div>
                    <p class="mt-1 text-xs text-gray-500">
                      <span v-if="isLoadingCaptcha">正在获取验证码...</span>
                      <span v-else-if="sessionData && sessionData.source === 'real'" class="text-green-600">
                        ✓ 已连接到真实教务系统，点击图片可刷新验证码
                      </span>
                      <span v-else-if="sessionData && sessionData.source === 'fallback'" class="text-yellow-600">
                        ⚠ 无法连接教务系统，使用演示验证码 (请输入 "DEMO" 或 "1234")
                      </span>
                      <span v-else-if="sessionData" class="text-blue-600">
                        点击验证码图片可刷新
                      </span>
                      <span v-else class="text-red-500">验证码加载失败，请点击重试</span>
                    </p>
                  </div>

                  <!-- Schedule Selection -->
                  <div class="space-y-3">
                    <label class="block text-sm font-medium leading-6 text-gray-900">
                      导入到哪个课表？ <span class="text-red-500">*</span>
                    </label>
                    
                    <div class="space-y-2">
                      <!-- Current schedule option -->
                      <label 
                        v-if="props.currentSchedule"
                        class="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                        :class="{ 'border-blue-500 bg-blue-50': form.action === 'use_current' }"
                      >
                        <input
                          type="radio"
                          name="schedule-action"
                          value="use_current"
                          v-model="form.action"
                          class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                        />
                        <div class="ml-3 flex-1">
                          <div class="text-sm font-medium text-gray-900">
                            导入到当前课表: {{ props.currentSchedule.name }}
                            <span class="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20 ml-2">
                              推荐
                            </span>
                          </div>
                          <div class="text-xs text-gray-500">将覆盖当前正在查看的课表中的课程</div>
                        </div>
                      </label>

                      <!-- Create new schedule option -->
                      <label class="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                             :class="{ 'border-blue-500 bg-blue-50': form.action === 'create_new' }">
                        <input
                          type="radio"
                          name="schedule-action"
                          value="create_new"
                          v-model="form.action"
                          class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                        />
                        <div class="ml-3 flex-1">
                          <div class="text-sm font-medium text-gray-900">创建新课表</div>
                          <div class="text-xs text-gray-500">将为导入的课程创建一个全新的课表</div>
                        </div>
                      </label>

                      <!-- New schedule name and start date inputs -->
                      <div v-if="form.action === 'create_new'" class="ml-7 space-y-3">
                        <input
                          v-model="form.scheduleName"
                          type="text"
                          placeholder="请输入新课表名称，如：2025春季学期"
                          class="block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm"
                        />
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-1">
                            开学日期（第一周的周一）
                          </label>
                          <input
                            v-model="form.startDate"
                            type="date"
                            class="block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm"
                          />
                          <p class="mt-1 text-xs text-gray-500">
                            请选择第一周周一的日期，课程时间将基于此日期计算
                          </p>
                        </div>
                      </div>

                      <!-- Use other existing schedule option -->
                      <label 
                        v-if="otherSchedules.length > 0"
                        class="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                        :class="{ 'border-blue-500 bg-blue-50': form.action === 'use_existing' }"
                      >
                        <input
                          type="radio"
                          name="schedule-action"
                          value="use_existing"
                          v-model="form.action"
                          class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                        />
                        <div class="ml-3 flex-1">
                          <div class="text-sm font-medium text-gray-900">导入到其他课表</div>
                          <div class="text-xs text-gray-500">选择其他已存在的课表进行导入</div>
                        </div>
                      </label>

                      <!-- Other schedules dropdown -->
                      <div v-if="form.action === 'use_existing' && otherSchedules.length > 0" class="ml-7">
                        <select
                          v-model="form.scheduleId"
                          class="block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm"
                        >
                          <option value="">请选择要导入的课表</option>
                          <option
                            v-for="schedule in otherSchedules"
                            :key="schedule.id"
                            :value="schedule.id"
                          >
                            {{ schedule.name }} ({{ schedule.status }})
                          </option>
                        </select>
                      </div>
                    </div>
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
                            <li>导入将覆盖选中课表中的现有课程数据</li>
                            <li>建议选择"导入到当前课表"以便直接查看导入结果</li>
                            <li>请确保网络连接正常</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- User Info Results -->
                <div v-if="userInfo" class="mt-4 rounded-md bg-blue-50 p-4">
                  <div class="flex">
                    <ExclamationCircleIcon class="h-5 w-5 text-blue-400" />
                    <div class="ml-3">
                      <h4 class="text-sm font-medium text-blue-800 mb-2">获取到的用户信息：</h4>
                      <div class="text-sm text-blue-700 space-y-2">
                        <div><strong>姓名：</strong>{{ userInfo.XM }}</div>
                        <div><strong>学号：</strong>{{ userInfo.XH }}</div>
                        <div><strong>班级：</strong>{{ userInfo.BJMC }}</div>
                        <div><strong>年级：</strong>{{ userInfo.XQM === '1' ? '大一' : userInfo.XQM === '2' ? '大二' : userInfo.XQM === '3' ? '大三' : userInfo.XQM === '4' ? '大四' : '其他' }}</div>
                        <div><strong>专业：</strong>{{ userInfo.ZYMC }}</div>
                        <div><strong>学年：</strong>{{ userInfo.XNMC }}</div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Success Message -->
                <div v-if="successMessage" class="mt-4 rounded-md bg-green-50 p-4">
                  <div class="flex">
                    <CheckCircleIcon class="h-5 w-5 text-green-400" />
                    <div class="ml-3">
                      <h3 class="text-sm font-medium text-green-800 whitespace-pre-line">
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
                <div class="mt-5 sm:mt-6">
                  <div class="sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                    <button
                      type="submit"
                      :disabled="isImporting || !form.username || !form.password || !form.captcha || !sessionData || isLoadingCaptcha"
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
import { ref, watch, computed } from 'vue';
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
  currentSchedule?: any; // 当前活跃的课表
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
  action: 'use_current', // 默认选择当前课表
  scheduleId: '',
  scheduleName: '',
  startDate: new Date().toISOString().split('T')[0], // 默认为今天
});

const isImporting = ref(false);
const importStatus = ref('');
const importProgress = ref(0);
const successMessage = ref('');
const errorMessage = ref('');
const userInfo = ref<any>(null);
const userSchedules = ref<any[]>([]);
const isLoadingSchedules = ref(false);
const sessionData = ref<{
  session_id: string;
  csrftoken: string;
  captcha_image: string;
} | null>(null);

// 计算属性：排除当前课表的其他课表
const otherSchedules = computed(() => {
  if (!props.currentSchedule) return userSchedules.value;
  return userSchedules.value.filter(schedule => schedule.id !== props.currentSchedule.id);
});

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

    // 根据选择的操作确定参数
    let apiAction = form.value.action;
    let scheduleId = undefined;
    let scheduleName = undefined;

    if (form.value.action === 'use_current' && props.currentSchedule) {
      apiAction = 'use_existing';
      scheduleId = props.currentSchedule.id;
    } else if (form.value.action === 'use_existing') {
      apiAction = 'use_existing';
      scheduleId = parseInt(form.value.scheduleId);
    } else if (form.value.action === 'create_new') {
      apiAction = 'create_new';
      scheduleName = form.value.scheduleName;
    }

    const response = await apiClient.importFromZFW({
      session_id: sessionData.value.session_id,
      username: form.value.username,
      password: form.value.password,
      captcha: form.value.captcha,
      action: apiAction,
      schedule_id: scheduleId,
      schedule_name: scheduleName,
      start_date: form.value.action === 'create_new' ? form.value.startDate : undefined,
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
      // 显示用户信息
      if (response.user_info) {
        userInfo.value = response.user_info;
      }
      
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


const isLoadingCaptcha = ref(false);

async function loadUserSchedules() {
  if (isLoadingSchedules.value) return;
  
  isLoadingSchedules.value = true;
  
  try {
    const response = await apiClient.getUserSchedules();
    userSchedules.value = response;
  } catch (error: any) {
    console.error('Failed to load user schedules:', error);
    errorMessage.value = '获取课表列表失败';
    userSchedules.value = [];
  } finally {
    isLoadingSchedules.value = false;
  }
}

async function refreshCaptcha() {
  if (isLoadingCaptcha.value) return; // 防止重复请求
  
  isLoadingCaptcha.value = true;
  errorMessage.value = '';
  
  try {
    const response = await apiClient.getImportSession();
    
    if (response && response.session_id && response.captcha_image) {
      sessionData.value = response;
      form.value.captcha = '';
      console.log('验证码加载成功');
    } else {
      throw new Error('验证码数据格式不正确');
    }
  } catch (error: any) {
    console.error('Failed to refresh captcha:', error);
    errorMessage.value = error.response?.data?.detail || '刷新验证码失败，请检查网络连接';
    sessionData.value = null;
  } finally {
    isLoadingCaptcha.value = false;
  }
}

// 监听模态框打开事件，自动获取验证码和课表列表
watch(() => props.isOpen, async (newValue, oldValue) => {
  if (newValue && !oldValue) {
    // 只有在从关闭到打开时才获取数据
    errorMessage.value = '';
    successMessage.value = '';
    
    // 根据是否有当前课表设置默认选项
    if (props.currentSchedule) {
      form.value.action = 'use_current';
    } else {
      form.value.action = 'create_new';
    }
    
    // 同时获取验证码和课表列表
    await Promise.all([
      refreshCaptcha(),
      loadUserSchedules()
    ]);
  } else if (!newValue && oldValue) {
    // 模态框关闭时重置状态
    resetForm();
  }
}, { immediate: false });

function resetForm() {
  form.value = {
    username: '',
    password: '',
    captcha: '',
    action: props.currentSchedule ? 'use_current' : 'create_new',
    scheduleId: '',
    scheduleName: '',
    startDate: new Date().toISOString().split('T')[0],
  };
  successMessage.value = '';
  errorMessage.value = '';
  userInfo.value = null;
  sessionData.value = null;
  userSchedules.value = [];
}
</script>
