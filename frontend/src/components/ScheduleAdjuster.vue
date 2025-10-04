<template>
  <div class="schedule-adjuster">
    <!-- 模态框覆盖层 -->
    <div v-if="isVisible" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click="closeModal">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4" @click.stop>
        <!-- 头部 -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">课表调休</h3>
          <button 
            @click="closeModal"
            class="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- 内容区域 -->
        <div class="p-6">
          <!-- 模式选择 -->
          <div class="mb-6">
            <div class="flex space-x-1 bg-gray-100 rounded-lg p-1">
              <button
                :class="[
                  'flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors',
                  adjustmentMode === 'swap' 
                    ? 'bg-white text-blue-600 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                ]"
                @click="adjustmentMode = 'swap'"
              >
                对调工作日
              </button>
              <button
                :class="[
                  'flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors',
                  adjustmentMode === 'holiday' 
                    ? 'bg-white text-blue-600 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                ]"
                @click="adjustmentMode = 'holiday'"
              >
                设置假期
              </button>
            </div>
          </div>

          <!-- 对调工作日模式 -->
          <div v-if="adjustmentMode === 'swap'" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                将此日期的课程
              </label>
              <input
                v-model="swapForm.fromDate"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                移动到此日期
              </label>
              <input
                v-model="swapForm.toDate"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>
            
            <button
              @click="confirmSwap"
              :disabled="!swapForm.fromDate || !swapForm.toDate || isLoading"
              :class="[
                'w-full px-4 py-2 bg-blue-600 text-white rounded-md font-medium transition-colors',
                !swapForm.fromDate || !swapForm.toDate || isLoading 
                  ? 'opacity-50 cursor-not-allowed' 
                  : 'hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500'
              ]"
            >
              <span v-if="isLoading" class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                处理中...
              </span>
              <span v-else>确认移动</span>
            </button>
          </div>

          <!-- 设置假期模式 -->
          <div v-if="adjustmentMode === 'holiday'" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                选择开始日期
              </label>
              <input
                v-model="holidayForm.startDate"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                选择结束日期（可选，留空则仅处理单日）
              </label>
              <input
                v-model="holidayForm.endDate"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                :min="holidayForm.startDate"
              />
            </div>
            
            <button
              @click="confirmHoliday"
              :disabled="!holidayForm.startDate || isLoading"
              :class="[
                'w-full px-4 py-2 bg-red-600 text-white rounded-md font-medium transition-colors',
                !holidayForm.startDate || isLoading 
                  ? 'opacity-50 cursor-not-allowed' 
                  : 'hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500'
              ]"
            >
              <span v-if="isLoading" class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                处理中...
              </span>
              <span v-else>确认放假</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 确认对话框 -->
    <div v-if="showConfirmDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-60">
      <div class="bg-white rounded-lg shadow-xl max-w-sm w-full mx-4">
        <div class="p-6">
          <div class="flex items-center mb-4">
            <div class="flex-shrink-0">
              <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.876c1.87 0 3.391-1.51 3.391-3.381 0-.685-.208-1.319-.564-1.847L15.75 7.878c-.355-.528-.83-.863-1.365-.863s-1.01.335-1.365.863L7.23 13.119c-.356.528-.564 1.162-.564 1.847C6.666 16.49 8.18 18 10.05 18z"/>
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-lg font-medium text-gray-900">确认操作</h3>
            </div>
          </div>
          <div class="mb-4">
            <p class="text-sm text-gray-600">{{ confirmMessage }}</p>
          </div>
          <div class="flex space-x-3">
            <button
              @click="showConfirmDialog = false"
              class="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
            >
              取消
            </button>
            <button
              @click="executeAdjustment"
              :class="[
                'flex-1 px-4 py-2 text-white rounded-md transition-colors',
                adjustmentMode === 'holiday' 
                  ? 'bg-red-600 hover:bg-red-700' 
                  : 'bg-blue-600 hover:bg-blue-700'
              ]"
            >
              确认
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

interface Props {
  isVisible: boolean;
  scheduleId: number;
}

interface Emits {
  (e: 'close'): void;
  (e: 'adjustment-applied'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// 响应式数据
const adjustmentMode = ref<'holiday' | 'swap'>('swap');
const isLoading = ref(false);
const showConfirmDialog = ref(false);

// 表单数据
const holidayForm = ref({
  startDate: '',
  endDate: ''
});

const swapForm = ref({
  fromDate: '',
  toDate: ''
});

// 计算属性
const confirmMessage = computed(() => {
  if (adjustmentMode.value === 'holiday') {
    if (holidayForm.value.endDate) {
      return `您确定要将 ${holidayForm.value.startDate} 到 ${holidayForm.value.endDate} 期间的所有课程设为不上课吗？此操作将隐藏这些日期的所有课程。`;
    } else {
      return `您确定要将 ${holidayForm.value.startDate} 的所有课程设为不上课吗？此操作将隐藏该日期的所有课程。`;
    }
  } else {
    return `您确定要将 ${swapForm.value.fromDate} 日期的课程全部移动到 ${swapForm.value.toDate}，并将 ${swapForm.value.fromDate} 日期清空吗？`;
  }
});

// 方法
const getTodayDate = () => {
  return new Date().toISOString().split('T')[0];
};

const closeModal = () => {
  emit('close');
  resetForms();
};

const resetForms = () => {
  holidayForm.value.startDate = '';
  holidayForm.value.endDate = '';
  swapForm.value.fromDate = '';
  swapForm.value.toDate = '';
  showConfirmDialog.value = false;
  isLoading.value = false;
};

const confirmHoliday = () => {
  if (!holidayForm.value.startDate) return;
  
  // 验证日期范围
  if (holidayForm.value.endDate && holidayForm.value.startDate > holidayForm.value.endDate) {
    alert('结束日期不能早于开始日期！');
    return;
  }
  
  showConfirmDialog.value = true;
};

const confirmSwap = () => {
  if (!swapForm.value.fromDate || !swapForm.value.toDate) return;
  if (swapForm.value.fromDate === swapForm.value.toDate) {
    alert('原日期和目标日期不能相同！');
    return;
  }
  showConfirmDialog.value = true;
};

const executeAdjustment = async () => {
  showConfirmDialog.value = false;
  isLoading.value = true;

  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('未找到登录凭证，请重新登录');
    }

    const url = `/api/schedules/${props.scheduleId}/adjustments`;
    
    let requestBody: any;
    if (adjustmentMode.value === 'holiday') {
      requestBody = {
        adjustment_type: 'HOLIDAY',
        holiday_date: holidayForm.value.startDate,
        end_date: holidayForm.value.endDate || null
      };
    } else {
      requestBody = {
        adjustment_type: 'SWAP',
        source_date: swapForm.value.fromDate,
        target_date: swapForm.value.toDate
      };
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem('access_token');
        throw new Error('登录已过期，请重新登录');
      }
      const errorData = await response.json();
      throw new Error(errorData.detail || '操作失败');
    }

    const result = await response.json();
    
    // 显示成功消息
    alert(result.message || '调休操作成功！');
    
    // 通知父组件刷新数据
    emit('adjustment-applied');
    
    // 关闭模态框
    closeModal();

  } catch (error) {
    console.error('Adjustment operation failed:', error);
    alert(error instanceof Error ? error.message : '调休操作失败，请重试。');
    
    // 如果是认证错误，可能需要重定向到登录页面
    if (error instanceof Error && error.message.includes('登录')) {
      setTimeout(() => {
        window.location.href = '/login';
      }, 2000);
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.z-60 {
  z-index: 60;
}
</style>
