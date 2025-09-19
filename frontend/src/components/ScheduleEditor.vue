<template>
  <div
    v-if="isOpen"
    class="relative z-50"
    aria-labelledby="modal-title"
    role="dialog"
    aria-modal="true"
  >
    <!-- Background backdrop -->
    <div
      class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
      @click="$emit('close')"
    ></div>

    <!-- Modal panel -->
    <div class="fixed inset-0 z-10 overflow-y-auto">
      <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
        <div
          class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl sm:p-6"
        >
          <!-- Header -->
          <div class="mb-6">
            <h3 class="text-lg font-semibold leading-6 text-gray-900" id="modal-title">
              {{ isEditing ? '编辑课表' : '创建课表' }}
            </h3>
          </div>

          <!-- Form -->
          <form @submit.prevent="handleSubmit">
            <div class="space-y-6">
              <!-- Basic Information -->
              <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                  <label for="name" class="block text-sm font-medium leading-6 text-gray-900">
                    课表名称 <span class="text-red-500">*</span>
                  </label>
                  <input
                    id="name"
                    v-model="formData.name"
                    type="text"
                    required
                    class="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                    placeholder="例：2024年春季学期"
                  />
                </div>

                <div>
                  <label for="status" class="block text-sm font-medium leading-6 text-gray-900">
                    状态
                  </label>
                  <select
                    id="status"
                    v-model="formData.status"
                    class="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                  >
                    <option value="进行">进行中</option>
                    <option value="结束">已结束</option>
                    <option value="隐藏">已隐藏</option>
                  </select>
                </div>

                <div>
                  <label for="start_date" class="block text-sm font-medium leading-6 text-gray-900">
                    开学日期 <span class="text-red-500">*</span>
                  </label>
                  <input
                    id="start_date"
                    v-model="formData.start_date"
                    type="date"
                    required
                    class="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                  />
                </div>

                <div>
                  <label for="total_weeks" class="block text-sm font-medium leading-6 text-gray-900">
                    总周数
                  </label>
                  <input
                    id="total_weeks"
                    v-model.number="formData.total_weeks"
                    type="number"
                    min="1"
                    max="52"
                    class="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                    placeholder="例：18"
                  />
                </div>
              </div>

              <!-- Class Times Configuration -->
              <div>
                <h4 class="text-base font-medium text-gray-900 mb-4">课程时间设置</h4>
                <div class="space-y-3">
                  <div
                    v-for="period in periods"
                    :key="period.number"
                    class="grid grid-cols-3 gap-4 items-center p-3 bg-gray-50 rounded-md"
                  >
                    <div class="text-sm font-medium text-gray-700">
                      第{{ period.number }}节
                    </div>
                    <div>
                      <label :for="`start-${period.number}`" class="sr-only">开始时间</label>
                      <input
                        :id="`start-${period.number}`"
                        v-model="formData.class_times[period.number].start"
                        type="time"
                        class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                      />
                    </div>
                    <div>
                      <label :for="`end-${period.number}`" class="sr-only">结束时间</label>
                      <input
                        :id="`end-${period.number}`"
                        v-model="formData.class_times[period.number].end"
                        type="time"
                        class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                      />
                    </div>
                  </div>
                </div>

                <!-- Reset to defaults button -->
                <div class="mt-4">
                  <button
                    type="button"
                    @click="resetToDefaults"
                    class="text-sm text-primary-600 hover:text-primary-500"
                  >
                    恢复默认时间设置
                  </button>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="mt-8 flex items-center justify-between">
              <div>
                <button
                  v-if="isEditing"
                  type="button"
                  @click="handleDelete"
                  class="inline-flex items-center gap-x-1.5 rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600"
                >
                  <TrashIcon class="h-4 w-4" />
                  删除课表
                </button>
              </div>
              
              <div class="flex items-center gap-3">
                <button
                  type="button"
                  @click="$emit('close')"
                  class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                >
                  取消
                </button>
                <button
                  type="submit"
                  :disabled="isSubmitting"
                  class="inline-flex items-center gap-x-1.5 rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <template v-if="isSubmitting">
                    <div class="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                    {{ isEditing ? '保存中...' : '创建中...' }}
                  </template>
                  <template v-else>
                    {{ isEditing ? '保存更改' : '创建课表' }}
                  </template>
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useScheduleStore } from '@/stores/schedule';
import { TrashIcon } from '@heroicons/vue/24/outline';
import type { ScheduleResponse, ScheduleCreate, ScheduleUpdate } from '@/types';

interface Props {
  isOpen: boolean;
  scheduleData?: ScheduleResponse | null;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  close: [];
  save: [];
}>();

const scheduleStore = useScheduleStore();

const isSubmitting = ref(false);

const isEditing = computed(() => !!props.scheduleData);

// Form data
const formData = ref<ScheduleCreate & { class_times: Record<string, { start: string; end: string }> }>({
  name: '',
  status: '进行',
  start_date: '',
  total_weeks: 18,
  class_times: {}
});

// Default periods (1-11 classes)
const periods = ref([
  { number: '1' },
  { number: '2' },
  { number: '3' },
  { number: '4' },
  { number: '5' },
  { number: '6' },
  { number: '7' },
  { number: '8' },
  { number: '9' },
  { number: '10' },
  { number: '11' },
]);

// Default class times
const defaultClassTimes = {
  '1': { start: '08:00', end: '08:45' },
  '2': { start: '08:55', end: '09:40' },
  '3': { start: '10:00', end: '10:45' },
  '4': { start: '10:55', end: '11:40' },
  '5': { start: '14:00', end: '14:45' },
  '6': { start: '14:55', end: '15:40' },
  '7': { start: '16:00', end: '16:45' },
  '8': { start: '16:55', end: '17:40' },
  '9': { start: '19:00', end: '19:45' },
  '10': { start: '19:55', end: '20:40' },
  '11': { start: '20:50', end: '21:35' },
};

// Initialize form data
function initializeForm() {
  if (props.scheduleData) {
    // Editing mode
    formData.value = {
      name: props.scheduleData.name,
      status: props.scheduleData.status,
      start_date: props.scheduleData.start_date,
      total_weeks: props.scheduleData.total_weeks,
      class_times: { ...defaultClassTimes, ...props.scheduleData.class_times }
    };
  } else {
    // Creating mode
    formData.value = {
      name: '',
      status: '进行',
      start_date: new Date().toISOString().split('T')[0],
      total_weeks: 18,
      class_times: { ...defaultClassTimes }
    };
  }
}

function resetToDefaults() {
  formData.value.class_times = { ...defaultClassTimes };
}

async function handleSubmit() {
  isSubmitting.value = true;
  
  try {
    const submitData: ScheduleCreate | ScheduleUpdate = {
      name: formData.value.name,
      status: formData.value.status,
      start_date: formData.value.start_date,
      total_weeks: formData.value.total_weeks,
      class_times: formData.value.class_times
    };

    if (isEditing.value && props.scheduleData) {
      await scheduleStore.updateSchedule(props.scheduleData.id, submitData);
    } else {
      await scheduleStore.createSchedule(submitData as ScheduleCreate);
    }
    
    emit('save');
  } catch (error) {
    console.error('Failed to save schedule:', error);
  } finally {
    isSubmitting.value = false;
  }
}

async function handleDelete() {
  if (!props.scheduleData) return;
  
  const confirmed = confirm(`确定要删除课表"${props.scheduleData.name}"吗？这将同时删除该课表下的所有事件。`);
  if (!confirmed) return;
  
  try {
    await scheduleStore.deleteSchedule(props.scheduleData.id);
    emit('save');
  } catch (error) {
    console.error('Failed to delete schedule:', error);
  }
}

// Watch for props changes to reinitialize form
watch(() => props.isOpen, (newValue) => {
  if (newValue) {
    initializeForm();
  }
});

// Initialize on mount
initializeForm();
</script>
