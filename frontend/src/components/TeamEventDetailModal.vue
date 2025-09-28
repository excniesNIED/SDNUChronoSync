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
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-4xl sm:p-6">
              <div v-if="event || relatedEvents.length > 0">
                <div class="flex items-start justify-between mb-6">
                  <div class="flex items-start">
                    <div
                      :style="{ backgroundColor: eventColor.bg }"
                      class="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full mr-4"
                    >
                      <CalendarIcon
                        :style="{ color: eventColor.text }"
                        class="h-6 w-6"
                        aria-hidden="true"
                      />
                    </div>
                    <div>
                      <DialogTitle as="h3" class="text-xl font-semibold leading-6 text-gray-900">
                        {{ primaryEvent?.title || '课程详情' }}
                      </DialogTitle>
                      <p v-if="primaryEvent?.instructor" class="text-sm text-gray-600 mt-1">
                        任课教师: {{ primaryEvent.instructor }}
                      </p>
                    </div>
                  </div>
                  
                  <!-- 关闭按钮 -->
                  <button
                    @click="$emit('close')"
                    class="rounded-md text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <span class="sr-only">关闭</span>
                    <XMarkIcon class="h-6 w-6" />
                  </button>
                </div>

                <!-- 课程基本信息 -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <!-- 课程时间信息 -->
                  <div class="bg-gray-50 rounded-lg p-4">
                    <h4 class="text-lg font-medium text-gray-900 mb-3 flex items-center">
                      <ClockIcon class="h-5 w-5 mr-2 text-gray-600" />
                      时间信息
                    </h4>
                    <div class="space-y-2 text-sm">
                      <div v-if="primaryEvent?.start_time" class="flex items-center">
                        <span class="text-gray-600 w-16">时间:</span>
                        <span>{{ formatDisplayDateTime(primaryEvent.start_time) }} - {{ formatDisplayTime(primaryEvent.end_time) }}</span>
                      </div>
                      <div v-if="primaryEvent?.weeks_display" class="flex items-center">
                        <span class="text-gray-600 w-16">周数:</span>
                        <span>{{ primaryEvent.weeks_display }}</span>
                      </div>
                      <div v-if="primaryEvent?.day_of_week || primaryEvent?.period" class="flex items-center">
                        <span class="text-gray-600 w-16">节次:</span>
                        <span>
                          <span v-if="primaryEvent?.day_of_week">{{ getDayOfWeekText(primaryEvent.day_of_week) }}</span>
                          <span v-if="primaryEvent?.day_of_week && primaryEvent?.period"> - </span>
                          <span v-if="primaryEvent?.period">{{ primaryEvent.period }}</span>
                        </span>
                      </div>
                      <div v-if="primaryEvent?.location" class="flex items-center">
                        <span class="text-gray-600 w-16">地点:</span>
                        <span>{{ primaryEvent.location }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- 统计信息 -->
                  <div class="bg-blue-50 rounded-lg p-4">
                    <h4 class="text-lg font-medium text-gray-900 mb-3 flex items-center">
                      <ChartBarIcon class="h-5 w-5 mr-2 text-blue-600" />
                      统计信息
                    </h4>
                    <div class="space-y-2 text-sm">
                      <div class="flex items-center justify-between">
                        <span class="text-gray-600">上课人数:</span>
                        <span class="font-medium text-blue-600">{{ allRelatedEvents.length }} 人</span>
                      </div>
                      <div class="flex items-center justify-between">
                        <span class="text-gray-600">课表数量:</span>
                        <span class="font-medium text-blue-600">{{ uniqueSchedules.length }} 个</span>
                      </div>
                      <div class="flex items-center justify-between">
                        <span class="text-gray-600">班级数量:</span>
                        <span class="font-medium text-blue-600">{{ uniqueClasses.length }} 个</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 上课成员列表 -->
                <div class="mb-6">
                  <h4 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
                    <UsersIcon class="h-5 w-5 mr-2 text-gray-600" />
                    上课成员 ({{ allRelatedEvents.length }} 人)
                  </h4>
                  
                  <!-- 按班级分组显示 -->
                  <div class="space-y-4">
                    <div
                      v-for="className in uniqueClasses"
                      :key="className"
                      class="border rounded-lg p-4"
                    >
                      <h5 class="font-medium text-gray-800 mb-3 flex items-center">
                        <span class="bg-primary-100 text-primary-800 px-2 py-1 rounded-full text-xs mr-2">
                          {{ className }}
                        </span>
                        共 {{ getEventsByClass(className).length }} 人
                      </h5>
                      
                      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                        <div
                          v-for="event in getEventsByClass(className)"
                          :key="event.id"
                          class="flex items-center p-3 bg-gray-50 rounded-md"
                        >
                          <div class="flex-1">
                            <div class="font-medium text-gray-900">
                              {{ event.owner?.full_name || '未知用户' }}
                            </div>
                            <div class="text-sm text-gray-600">
                              学号: {{ event.owner?.student_id || '未知' }}
                            </div>
                            <div class="text-xs text-gray-500 mt-1">
                              课表: {{ getScheduleName(event) }}
                            </div>
                          </div>
                          <div
                            :style="{ backgroundColor: getUserColor(event.owner?.id || event.schedule_id).bg }"
                            class="w-3 h-3 rounded-full ml-2"
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 课程描述 -->
                <div v-if="primaryEvent?.description" class="mb-6">
                  <h4 class="text-lg font-medium text-gray-900 mb-3 flex items-center">
                    <DocumentTextIcon class="h-5 w-5 mr-2 text-gray-600" />
                    课程描述
                  </h4>
                  <div class="bg-gray-50 rounded-lg p-4">
                    <p class="text-gray-700 whitespace-pre-wrap">{{ primaryEvent.description }}</p>
                  </div>
                </div>

                <!-- 操作按钮 -->
                <div class="flex justify-end pt-4 border-t">
                  <button
                    type="button"
                    @click="$emit('close')"
                    class="inline-flex justify-center rounded-md bg-white px-6 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                  >
                    关闭
                  </button>
                </div>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue';
import {
  CalendarIcon,
  ClockIcon,
  MapPinIcon,
  UsersIcon,
  DocumentTextIcon,
  XMarkIcon,
  ChartBarIcon,
} from '@heroicons/vue/24/outline';
import { formatDisplayDateTime, formatDisplayTime } from '@/utils/date';
import { getUserColor } from '@/utils/colors';
import type { Event } from '@/types';

interface Props {
  isOpen: boolean;
  event?: Event | null;
  relatedEvents?: Event[];
}

const props = withDefaults(defineProps<Props>(), {
  relatedEvents: () => []
});

defineEmits<{
  close: [];
}>();

// 主要事件（用于显示基本信息）
const primaryEvent = computed(() => {
  return props.event || (props.relatedEvents.length > 0 ? props.relatedEvents[0] : null);
});

// 所有相关事件（包括主事件）
const allRelatedEvents = computed(() => {
  const events = [...props.relatedEvents];
  if (props.event && !events.some(e => e.id === props.event!.id)) {
    events.push(props.event);
  }
  return events.filter(e => e.owner); // 确保有owner信息
});

// 事件颜色
const eventColor = computed(() => {
  if (!primaryEvent.value) return { bg: '#f3f4f6', text: '#374151' };
  const userId = primaryEvent.value.owner?.id || primaryEvent.value.schedule_id || 0;
  return getUserColor(userId);
});

// 获取唯一的班级列表
const uniqueClasses = computed(() => {
  const classes = new Set<string>();
  allRelatedEvents.value.forEach(event => {
    if (event.owner?.class_name) {
      classes.add(event.owner.class_name);
    }
  });
  return Array.from(classes).sort();
});

// 获取唯一的课表数量
const uniqueSchedules = computed(() => {
  const scheduleIds = new Set<number>();
  allRelatedEvents.value.forEach(event => {
    scheduleIds.add(event.schedule_id);
  });
  return Array.from(scheduleIds);
});

// 根据班级获取事件
function getEventsByClass(className: string): Event[] {
  return allRelatedEvents.value
    .filter(event => event.owner?.class_name === className)
    .sort((a, b) => {
      const nameA = a.owner?.full_name || '';
      const nameB = b.owner?.full_name || '';
      return nameA.localeCompare(nameB);
    });
}

// 获取星期几的中文显示
function getDayOfWeekText(dayOfWeek: number): string {
  const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
  return days[dayOfWeek] || '未知';
}

// 获取课表名称（这里需要从某个地方获取课表信息）
function getScheduleName(event: Event): string {
  // 这里可能需要从课表store或其他地方获取课表名称
  // 暂时返回课表ID
  return `课表 ${event.schedule_id}`;
}
</script>
