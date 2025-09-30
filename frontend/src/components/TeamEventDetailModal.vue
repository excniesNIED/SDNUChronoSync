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
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-4xl">
              <div v-if="event || relatedEvents.length > 0">
                <!-- 头部 -->
                <div class="flex items-start justify-between px-4 sm:px-6 pt-5 pb-4 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white">
                  <div class="flex items-start gap-3">
                    <div
                      :style="{ backgroundColor: eventColor.bg }"
                      class="flex h-12 w-12 sm:h-14 sm:w-14 flex-shrink-0 items-center justify-center rounded-xl shadow-sm"
                    >
                      <CalendarIcon
                        :style="{ color: eventColor.text }"
                        class="h-6 w-6 sm:h-7 sm:w-7"
                        aria-hidden="true"
                      />
                    </div>
                    <div class="flex-1 min-w-0">
                      <DialogTitle as="h3" class="text-lg sm:text-xl font-bold leading-6 text-gray-900">
                        {{ primaryEvent?.title || '课程详情' }}
                      </DialogTitle>
                      <p v-if="primaryEvent?.instructor" class="text-sm text-gray-600 mt-1.5 flex items-center gap-1.5">
                        <UserCircleIcon class="h-4 w-4 text-gray-400" />
                        任课教师: <span class="font-medium">{{ primaryEvent.instructor }}</span>
                      </p>
                    </div>
                  </div>
                  
                  <!-- 关闭按钮 -->
                  <button
                    @click="$emit('close')"
                    class="rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 p-1.5 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <span class="sr-only">关闭</span>
                    <XMarkIcon class="h-5 w-5" />
                  </button>
                </div>

                <!-- 内容区域 -->
                <div class="px-4 sm:px-6 py-5 space-y-6">
                  <!-- 课程基本信息 -->
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- 课程时间信息 -->
                    <div class="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-4 border border-gray-200">
                      <h4 class="text-base font-semibold text-gray-900 mb-3 flex items-center">
                        <ClockIcon class="h-5 w-5 mr-2 text-indigo-600" />
                        时间信息
                      </h4>
                      <div class="space-y-2.5 text-sm">
                        <div v-if="primaryEvent?.start_time" class="flex items-start">
                          <span class="text-gray-600 font-medium w-14 flex-shrink-0">时间</span>
                          <span class="text-gray-900">{{ formatDisplayDateTime(primaryEvent.start_time) }} - {{ formatDisplayTime(primaryEvent.end_time) }}</span>
                        </div>
                        <div v-if="primaryEvent?.weeks_display" class="flex items-start">
                          <span class="text-gray-600 font-medium w-14 flex-shrink-0">周数</span>
                          <span class="text-gray-900">{{ primaryEvent.weeks_display }}</span>
                        </div>
                        <div v-if="primaryEvent?.day_of_week || primaryEvent?.period" class="flex items-start">
                          <span class="text-gray-600 font-medium w-14 flex-shrink-0">节次</span>
                          <span class="text-gray-900">
                            <span v-if="primaryEvent?.day_of_week">{{ getDayOfWeekText(primaryEvent.day_of_week) }}</span>
                            <span v-if="primaryEvent?.day_of_week && primaryEvent?.period"> · </span>
                            <span v-if="primaryEvent?.period">{{ primaryEvent.period }}</span>
                          </span>
                        </div>
                        <div v-if="primaryEvent?.location" class="flex items-start">
                          <span class="text-gray-600 font-medium w-14 flex-shrink-0">地点</span>
                          <span class="text-gray-900 flex items-center gap-1">
                            <MapPinIcon class="h-3.5 w-3.5 text-gray-400" />
                            {{ primaryEvent.location }}
                          </span>
                        </div>
                      </div>
                    </div>

                    <!-- 统计信息 -->
                    <div class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-200">
                      <h4 class="text-base font-semibold text-gray-900 mb-3 flex items-center">
                        <ChartBarIcon class="h-5 w-5 mr-2 text-blue-600" />
                        统计信息
                      </h4>
                      <div class="space-y-3 text-sm">
                        <div class="flex items-center justify-between py-1.5">
                          <span class="text-gray-700 font-medium">上课人数</span>
                          <span class="inline-flex items-center gap-1 font-semibold text-blue-700">
                            <UsersIcon class="h-4 w-4" />
                            {{ allRelatedEvents.length }} 人
                          </span>
                        </div>
                        <div class="flex items-center justify-between py-1.5">
                          <span class="text-gray-700 font-medium">课表数量</span>
                          <span class="inline-flex items-center gap-1 font-semibold text-indigo-700">
                            <CalendarDaysIcon class="h-4 w-4" />
                            {{ uniqueSchedules.length }} 个
                          </span>
                        </div>
                        <div class="flex items-center justify-between py-1.5">
                          <span class="text-gray-700 font-medium">班级数量</span>
                          <span class="inline-flex items-center gap-1 font-semibold text-purple-700">
                            <AcademicCapIcon class="h-4 w-4" />
                            {{ uniqueClasses.length }} 个
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- 上课成员列表 -->
                  <div>
                    <h4 class="text-base font-semibold text-gray-900 mb-3 flex items-center">
                      <UsersIcon class="h-5 w-5 mr-2 text-gray-600" />
                      上课成员 
                      <span class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                        {{ allRelatedEvents.length }} 人
                      </span>
                    </h4>
                    
                    <!-- 按班级分组显示 -->
                    <div class="space-y-4">
                      <div
                        v-for="className in uniqueClasses"
                        :key="className"
                        class="border border-gray-200 rounded-xl overflow-hidden"
                      >
                        <div class="bg-gradient-to-r from-primary-50 to-blue-50 px-4 py-2.5 border-b border-gray-200">
                          <h5 class="font-semibold text-gray-800 flex items-center">
                            <span class="bg-primary-600 text-white px-2.5 py-1 rounded-lg text-xs mr-2">
                              {{ className }}
                            </span>
                            共 {{ getEventsByClass(className).length }} 人
                          </h5>
                        </div>
                        
                        <div class="p-3 bg-white">
                          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                            <div
                              v-for="event in getEventsByClass(className)"
                              :key="event.id"
                              class="flex items-center p-3 bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors"
                            >
                              <UserAvatar 
                                :user="event.owner" 
                                size="sm"
                                class="mr-3 flex-shrink-0"
                              />
                              <div class="flex-1 min-w-0">
                                <div class="font-medium text-gray-900 truncate">
                                  {{ event.owner?.full_name || '未知用户' }}
                                </div>
                                <div class="text-xs text-gray-600 truncate">
                                  {{ event.owner?.student_id || '未知' }}
                                </div>
                                <div class="text-xs text-gray-500 mt-0.5 truncate">
                                  {{ getScheduleName(event) }}
                                </div>
                              </div>
                              <div
                                :style="{ backgroundColor: getUserColor(event.owner?.id || event.schedule_id).bg }"
                                class="w-2.5 h-2.5 rounded-full ml-2 flex-shrink-0"
                              ></div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- 课程描述 -->
                  <div v-if="primaryEvent?.description">
                    <h4 class="text-base font-semibold text-gray-900 mb-3 flex items-center">
                      <DocumentTextIcon class="h-5 w-5 mr-2 text-gray-600" />
                      课程描述
                    </h4>
                    <div class="bg-amber-50 border border-amber-200 rounded-xl p-4">
                      <p class="text-gray-800 text-sm leading-relaxed whitespace-pre-wrap">{{ primaryEvent.description }}</p>
                    </div>
                  </div>
                </div>

                <!-- 底部操作栏 -->
                <div class="flex justify-end gap-3 px-4 sm:px-6 py-4 bg-gray-50 border-t border-gray-200">
                  <button
                    type="button"
                    @click="$emit('close')"
                    class="inline-flex items-center justify-center gap-1.5 rounded-lg bg-white px-5 py-2.5 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-100 transition-colors"
                  >
                    <XMarkIcon class="h-4 w-4" />
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
  UserCircleIcon,
  CalendarDaysIcon,
  AcademicCapIcon,
} from '@heroicons/vue/24/outline';
import { formatDisplayDateTime, formatDisplayTime } from '@/utils/date';
import { getUserColor } from '@/utils/colors';
import UserAvatar from './UserAvatar.vue';
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

// 获取课表名称
function getScheduleName(event: Event): string {
  // 如果事件有 schedule 信息，使用课表名称
  if (event.schedule?.name) {
    return event.schedule.name;
  }
  
  // 否则使用默认格式
  return `课表 ${event.schedule_id}`;
}
</script>
