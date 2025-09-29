<template>
  <TransitionRoot as="template" :show="isOpen">
    <Dialog as="div" class="relative z-50" @close="$emit('close')">
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
              <form @submit.prevent="handleSubmit">
                <div>
                  <div class="text-center">
                    <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">
                      {{ isEditMode ? '编辑日程' : '创建日程' }}
                    </DialogTitle>
                  </div>

                  <div class="mt-6 space-y-4">
                    <!-- Title -->
                    <div>
                      <label for="title" class="block text-sm font-medium leading-6 text-gray-900">
                        标题 <span class="text-red-500">*</span>
                      </label>
                      <input
                        id="title"
                        v-model="form.title"
                        type="text"
                        required
                        class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                        placeholder="请输入日程标题"
                      />
                    </div>

                    <!-- Description -->
                    <div>
                      <label for="description" class="block text-sm font-medium leading-6 text-gray-900">
                        描述
                      </label>
                      <textarea
                        id="description"
                        v-model="form.description"
                        rows="3"
                        class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                        placeholder="请输入日程描述"
                      />
                    </div>

                    <!-- Location -->
                    <div>
                      <label for="location" class="block text-sm font-medium leading-6 text-gray-900">
                        地点
                      </label>
                      <input
                        id="location"
                        v-model="form.location"
                        type="text"
                        class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                        placeholder="请输入地点"
                      />
                    </div>

                    <!-- Instructor -->
                    <div>
                      <label for="instructor" class="block text-sm font-medium leading-6 text-gray-900">
                        教师
                      </label>
                      <input
                        id="instructor"
                        v-model="form.instructor"
                        type="text"
                        class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                        placeholder="请输入教师姓名"
                      />
                    </div>

                    <!-- Course Details -->
                    <div class="space-y-4">
                      <!-- Week Input Method Toggle -->
                      <div>
                        <label class="block text-sm font-medium leading-6 text-gray-900 mb-2">
                          周数设置
                        </label>
                        <div class="flex gap-4 mb-3">
                          <label class="inline-flex items-center">
                            <input
                              v-model="weekInputMode"
                              type="radio"
                              value="simple"
                              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300"
                            >
                            <span class="ml-2 text-sm text-gray-700">简单输入</span>
                          </label>
                          <label class="inline-flex items-center">
                            <input
                              v-model="weekInputMode"
                              type="radio"
                              value="advanced"
                              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300"
                            >
                            <span class="ml-2 text-sm text-gray-700">高级输入</span>
                          </label>
                        </div>
                        
                        <!-- Simple Week Input -->
                        <div v-if="weekInputMode === 'simple'" class="grid grid-cols-2 gap-2">
                          <div>
                            <label for="week_start" class="block text-xs text-gray-600">开始周</label>
                            <input
                              id="week_start"
                              v-model.number="form.week_start"
                              type="number"
                              min="1"
                              max="25"
                              class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm"
                              placeholder="1"
                            />
                          </div>
                          <div>
                            <label for="week_end" class="block text-xs text-gray-600">结束周</label>
                            <input
                              id="week_end"
                              v-model.number="form.week_end"
                              type="number"
                              min="1"
                              max="25"
                              class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm"
                              placeholder="16"
                            />
                          </div>
                        </div>
                        
                        <!-- Advanced Week Input -->
                        <div v-else>
                          <input
                            id="weeks_input"
                            v-model="form.weeks_input"
                            type="text"
                            class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                            placeholder="例：1,3-5,7,9-16"
                          />
                          <p class="mt-1 text-xs text-gray-500">
                            支持格式：单周(1)、连续周(3-5)、多段组合(1,3-5,7)
                          </p>
                        </div>
                      </div>

                      <!-- Period Selection -->
                      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                        <div>
                          <label class="block text-sm font-medium leading-6 text-gray-900 mb-2">
                            节次选择
                          </label>
                          <div class="flex gap-2 mb-2">
                            <select
                              v-model.number="form.period_start"
                              @change="updateTimeFromPeriod"
                              class="block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm"
                            >
                              <option value="">开始节</option>
                              <option v-for="n in 11" :key="n" :value="n">第{{ n }}节</option>
                            </select>
                            <select
                              v-model.number="form.period_end"
                              @change="updateTimeFromPeriod"
                              class="block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm"
                            >
                              <option value="">结束节</option>
                              <option v-for="n in 11" :key="n" :value="n">第{{ n }}节</option>
                            </select>
                          </div>
                          <p class="text-xs text-gray-500">
                            选择节次将自动填充时间
                          </p>
                        </div>
                        
                        <div>
                          <label for="day_of_week" class="block text-sm font-medium leading-6 text-gray-900">
                            星期
                          </label>
                          <select
                            id="day_of_week"
                            v-model.number="form.day_of_week"
                            class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm"
                          >
                            <option value="">选择星期</option>
                            <option :value="1">星期一</option>
                            <option :value="2">星期二</option>
                            <option :value="3">星期三</option>
                            <option :value="4">星期四</option>
                            <option :value="5">星期五</option>
                            <option :value="6">星期六</option>
                            <option :value="7">星期日</option>
                          </select>
                        </div>
                      </div>
                    </div>

                    <!-- Time Input (HHMM only) -->
                    <div class="space-y-4">
                      <!-- Date Display (read-only, calculated from week and day) -->
                      <div v-if="calculatedDate">
                        <label class="block text-sm font-medium leading-6 text-gray-900">
                          计算的日期
                        </label>
                        <div class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 bg-gray-50 text-gray-700 text-sm">
                          {{ formatCalculatedDate(calculatedDate) }}
                        </div>
                      </div>
                      
                      <!-- Time inputs -->
                      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                        <div>
                          <label for="start_time_input" class="block text-sm font-medium leading-6 text-gray-900">
                            开始时间 <span class="text-red-500">*</span>
                          </label>
                          <input
                            id="start_time_input"
                            v-model="form.start_time_only"
                            type="time"
                            required
                            class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                          />
                        </div>
                        <div>
                          <label for="end_time_input" class="block text-sm font-medium leading-6 text-gray-900">
                            结束时间 <span class="text-red-500">*</span>
                          </label>
                          <input
                            id="end_time_input"
                            v-model="form.end_time_only"
                            type="time"
                            required
                            class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                          />
                        </div>
                      </div>
                    </div>

                  </div>
                </div>

                <!-- Error message -->
                <div v-if="error" class="mt-4 rounded-md bg-red-50 p-4">
                  <div class="flex">
                    <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
                    <div class="ml-3">
                      <h3 class="text-sm font-medium text-red-800">
                        {{ error }}
                      </h3>
                    </div>
                  </div>
                </div>

                <!-- Actions -->
                <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                  <button
                    type="submit"
                    :disabled="isLoading"
                    class="inline-flex w-full justify-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600 disabled:opacity-50 disabled:cursor-not-allowed sm:col-start-2"
                  >
                    <span v-if="isLoading" class="mr-2">
                      <div class="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                    </span>
                    {{ isLoading ? '保存中...' : '保存' }}
                  </button>
                  <button
                    type="button"
                    @click="$emit('close')"
                    class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0"
                  >
                    取消
                  </button>
                </div>

                <!-- Delete button (for existing events) -->
                <div v-if="isEditMode && onDelete" class="mt-4 pt-4 border-t border-gray-200">
                  <button
                    type="button"
                    @click="handleDelete"
                    class="inline-flex w-full justify-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600"
                  >
                    删除日程
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
import { ref, computed, watch } from 'vue';
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue';
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline';
import { formatDateTime, formatDisplayDate } from '@/utils/date';
import { useScheduleStore } from '@/stores/schedule';
import type { Event } from '@/types';

interface Props {
  isOpen: boolean;
  event?: Event | null;
  isAdmin?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  isAdmin: false,
});

const emit = defineEmits<{
  close: [];
  save: [eventData: any];
  delete?: [eventId: number];
}>();

const isLoading = ref(false);
const error = ref<string | null>(null);

const scheduleStore = useScheduleStore();

const form = ref({
  title: '',
  description: '',
  location: '',
  start_time: '',
  end_time: '',
  start_time_only: '',
  end_time_only: '',
  instructor: '',
  weeks_display: '',
  weeks_input: '',
  week_start: undefined as number | undefined,
  week_end: undefined as number | undefined,
  day_of_week: undefined as number | undefined,
  period: '',
  period_start: undefined as number | undefined,
  period_end: undefined as number | undefined,
});

const weekInputMode = ref<'simple' | 'advanced'>('simple');

// 课程时间表配置
const classTimes = ref({
  "1": { start: "08:00", end: "08:45" },
  "2": { start: "08:50", end: "09:35" },
  "3": { start: "09:50", end: "10:35" },
  "4": { start: "10:40", end: "11:25" },
  "5": { start: "11:30", end: "12:15" },
  "6": { start: "14:00", end: "14:45" },
  "7": { start: "14:50", end: "15:35" },
  "8": { start: "15:50", end: "16:35" },
  "9": { start: "16:40", end: "17:25" },
  "10": { start: "19:00", end: "19:45" },
  "11": { start: "19:50", end: "20:35" }
});

const isEditMode = computed(() => props.event && props.event.id > 0);
const onDelete = computed(() => emit);

// 计算具体日期：基于课表开始日期、周数和星期几
const calculatedDate = computed(() => {
  const schedule = scheduleStore.activeSchedule;
  if (!schedule || !schedule.start_date || !form.value.week_start || !form.value.day_of_week) {
    return null;
  }
  
  // 使用第一个选中的周数
  const weekNumber = form.value.week_start;
  const dayOfWeek = form.value.day_of_week;
  
  // 计算具体日期
  const scheduleStartDate = new Date(schedule.start_date);
  
  // 计算从课表开始到目标周的天数
  // 周一=1对应offset=0，周二=2对应offset=1，...，周日=7对应offset=6
  const dayOffset = dayOfWeek - 1;
  const totalDays = (weekNumber - 1) * 7 + dayOffset;
  
  const targetDate = new Date(scheduleStartDate);
  targetDate.setDate(scheduleStartDate.getDate() + totalDays);
  
  return targetDate;
});

// 格式化计算出的日期
function formatCalculatedDate(date: Date): string {
  return formatDisplayDate(date);
}

// 根据节次自动填充时间
function updateTimeFromPeriod() {
  if (form.value.period_start && form.value.period_end) {
    const startPeriod = classTimes.value[form.value.period_start.toString()];
    const endPeriod = classTimes.value[form.value.period_end.toString()];
    
    if (startPeriod && endPeriod) {
      // 直接使用时间字符串
      form.value.start_time_only = startPeriod.start;
      form.value.end_time_only = endPeriod.end;
      
      // 更新period显示
      if (form.value.period_start === form.value.period_end) {
        form.value.period = `第${form.value.period_start}节`;
      } else {
        form.value.period = `第${form.value.period_start}-${form.value.period_end}节`;
      }
    }
  }
}

// 格式化周数显示
function formatWeeksDisplay() {
  if (weekInputMode.value === 'simple') {
    if (form.value.week_start && form.value.week_end) {
      if (form.value.week_start === form.value.week_end) {
        form.value.weeks_display = `第${form.value.week_start}周`;
        form.value.weeks_input = form.value.week_start.toString();
      } else {
        form.value.weeks_display = `第${form.value.week_start}-${form.value.week_end}周`;
        form.value.weeks_input = `${form.value.week_start}-${form.value.week_end}`;
      }
    }
  } else {
    // 高级模式，直接使用用户输入
    if (form.value.weeks_input) {
      form.value.weeks_display = `第${form.value.weeks_input}周`;
    }
  }
}

// Watch for event changes to populate form
watch(() => props.event, (newEvent) => {
  if (newEvent) {
    // 解析现有事件的时间部分
    const startTime = newEvent.start_time ? new Date(newEvent.start_time) : new Date();
    const endTime = newEvent.end_time ? new Date(newEvent.end_time) : new Date(startTime.getTime() + 60 * 60 * 1000);
    
    form.value = {
      title: newEvent.title || '',
      description: newEvent.description || '',
      location: newEvent.location || '',
      start_time: newEvent.start_time ? formatDateTime(newEvent.start_time) : '',
      end_time: newEvent.end_time ? formatDateTime(newEvent.end_time) : '',
      start_time_only: startTime.toTimeString().slice(0, 5), // HH:MM格式
      end_time_only: endTime.toTimeString().slice(0, 5), // HH:MM格式
      instructor: newEvent.instructor || '',
      weeks_display: newEvent.weeks_display || '',
      weeks_input: newEvent.weeks_input || '',
      week_start: undefined,
      week_end: undefined,
      day_of_week: newEvent.day_of_week,
      period: newEvent.period || '',
      period_start: undefined,
      period_end: undefined,
    };
    
    // 解析已有的节次信息
    if (newEvent.period) {
      const periodMatch = newEvent.period.match(/第?(\d+)(?:-(\d+))?节?/);
      if (periodMatch) {
        form.value.period_start = parseInt(periodMatch[1]);
        form.value.period_end = parseInt(periodMatch[2] || periodMatch[1]);
      }
    }
    
    // 解析已有的周数信息
    if (newEvent.weeks_input || newEvent.weeks_display) {
      const weeksStr = newEvent.weeks_input || newEvent.weeks_display;
      if (weeksStr.includes(',') || weeksStr.match(/\d+-\d+/)) {
        weekInputMode.value = 'advanced';
        form.value.weeks_input = weeksStr.replace(/第|周/g, '');
      } else {
        weekInputMode.value = 'simple';
        const weekMatch = weeksStr.match(/(\d+)(?:-(\d+))?/);
        if (weekMatch) {
          form.value.week_start = parseInt(weekMatch[1]);
          form.value.week_end = parseInt(weekMatch[2] || weekMatch[1]);
        }
      }
    } else if (!form.value.week_start && !form.value.day_of_week) {
      // 如果没有周数信息，尝试从事件时间计算
      if (newEvent.start_time && scheduleStore.activeSchedule?.start_date) {
        const eventDate = new Date(newEvent.start_time);
        const scheduleStartDate = new Date(scheduleStore.activeSchedule.start_date);
        const daysDiff = Math.floor((eventDate.getTime() - scheduleStartDate.getTime()) / (1000 * 60 * 60 * 24));
        const weekNumber = Math.floor(daysDiff / 7) + 1;
        const dayOfWeek = eventDate.getDay() === 0 ? 7 : eventDate.getDay();
        
        form.value.week_start = weekNumber;
        form.value.week_end = weekNumber;
        form.value.day_of_week = dayOfWeek;
      }
    }
  } else {
    // Reset form for new event - 设置默认时间
    form.value = {
      title: '',
      description: '',
      location: '',
      start_time: '',
      end_time: '',
      start_time_only: '08:20', // 默认第一节课开始时间
      end_time_only: '09:05',   // 默认第一节课结束时间
      instructor: '',
      weeks_display: '',
      weeks_input: '',
      week_start: 1, // 默认第1周
      week_end: 1,
      day_of_week: 1, // 默认周一
      period: '',
      period_start: undefined,
      period_end: undefined,
    };
    
    weekInputMode.value = 'simple';
  }
  error.value = null;
}, { immediate: true });

// 监听周数变化自动格式化
watch([() => form.value.week_start, () => form.value.week_end, () => form.value.weeks_input, weekInputMode], formatWeeksDisplay);

async function handleSubmit() {
  error.value = null;
  
  // Validation
  if (!form.value.title.trim()) {
    error.value = '请输入日程标题';
    return;
  }
  
  if (!form.value.start_time_only || !form.value.end_time_only) {
    error.value = '请选择开始和结束时间';
    return;
  }
  
  if (!form.value.week_start || !form.value.day_of_week) {
    error.value = '请选择周数和星期';
    return;
  }
  
  // 验证时间逻辑
  const [startHour, startMinute] = form.value.start_time_only.split(':').map(Number);
  const [endHour, endMinute] = form.value.end_time_only.split(':').map(Number);
  
  if (startHour * 60 + startMinute >= endHour * 60 + endMinute) {
    error.value = '结束时间必须晚于开始时间';
    return;
  }
  
  // 构造完整的日期时间
  const targetDate = calculatedDate.value;
  if (!targetDate) {
    error.value = '无法计算日期，请检查课表设置';
    return;
  }
  
  const startDateTime = new Date(targetDate);
  startDateTime.setHours(startHour, startMinute, 0, 0);
  
  const endDateTime = new Date(targetDate);
  endDateTime.setHours(endHour, endMinute, 0, 0);
  
  isLoading.value = true;
  
  try {
    // 确保格式化周数和节次
    formatWeeksDisplay();
    
    const eventData = {
      title: form.value.title.trim(),
      description: form.value.description?.trim() || undefined,
      location: form.value.location?.trim() || undefined,
      start_time: startDateTime.toISOString(),
      end_time: endDateTime.toISOString(),
      instructor: form.value.instructor?.trim() || undefined,
      weeks_display: form.value.weeks_display?.trim() || undefined,
      weeks_input: form.value.weeks_input?.trim() || undefined,
      day_of_week: form.value.day_of_week,
      period: form.value.period?.trim() || undefined,
    };
    
    emit('save', eventData);
  } catch (err: any) {
    error.value = err.message || '保存失败，请重试';
  } finally {
    isLoading.value = false;
  }
}

function handleDelete() {
  if (props.event?.id && emit) {
    emit('delete', props.event.id);
  }
}
</script>
