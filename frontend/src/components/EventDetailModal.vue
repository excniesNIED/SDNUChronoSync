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
              <div v-if="event">
                <div class="sm:flex sm:items-start">
                  <div
                    :style="{ backgroundColor: eventColor.bg }"
                    class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full sm:mx-0 sm:h-10 sm:w-10"
                  >
                    <CalendarIcon
                      :style="{ color: eventColor.text }"
                      class="h-6 w-6"
                      aria-hidden="true"
                    />
                  </div>
                  <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left flex-1">
                    <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">
                      {{ event.title }}
                    </DialogTitle>
                    <div class="mt-2 space-y-3">
                      <!-- Owner Information -->
                      <div v-if="event.owner" class="flex items-center text-sm text-gray-600">
                        <UserIcon class="h-4 w-4 mr-2 text-gray-400" />
                        <span>{{ event.owner.full_name }} ({{ event.owner.class_name }})</span>
                      </div>

                      <!-- Instructor Information -->
                      <div v-if="event.instructor" class="flex items-center text-sm text-gray-600">
                        <AcademicCapIcon class="h-4 w-4 mr-2 text-gray-400" />
                        <span>任课教师: {{ event.instructor }}</span>
                      </div>

                      <!-- Time Information -->
                      <div class="flex items-center text-sm text-gray-600">
                        <ClockIcon class="h-4 w-4 mr-2 text-gray-400" />
                        <div>
                          <div>{{ formatDisplayDateTime(event.start_time) }}</div>
                          <div class="text-xs text-gray-500">
                            至 {{ formatDisplayDateTime(event.end_time) }}
                          </div>
                        </div>
                      </div>

                      <!-- Course Schedule Information -->
                      <div v-if="event.weeks_display || event.day_of_week || event.period" class="bg-blue-50 rounded-lg p-4 space-y-3">
                        <h4 class="text-sm font-medium text-blue-800 mb-2">课程安排</h4>
                        
                        <!-- Week Information -->
                        <div v-if="event.weeks_display" class="flex items-center text-sm text-gray-700">
                          <CalendarDaysIcon class="h-4 w-4 mr-2 text-blue-500" />
                          <span class="font-medium">上课周数:</span>
                          <span class="ml-2 px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                            {{ event.weeks_display }}
                          </span>
                        </div>

                        <!-- Day and Period Information -->
                        <div v-if="event.day_of_week || event.period" class="flex items-center text-sm text-gray-700">
                          <BookmarkIcon class="h-4 w-4 mr-2 text-blue-500" />
                          <span class="font-medium">上课时间:</span>
                          <span class="ml-2 px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                            <span v-if="event.day_of_week">{{ getDayOfWeekText(event.day_of_week) }}</span>
                            <span v-if="event.day_of_week && event.period"> • </span>
                            <span v-if="event.period">{{ event.period }}</span>
                          </span>
                        </div>
                      </div>

                      <!-- Location -->
                      <div v-if="event.location" class="bg-green-50 rounded-lg p-4">
                        <h4 class="text-sm font-medium text-green-800 mb-2">上课地点</h4>
                        <div class="flex items-center text-sm text-gray-700">
                          <MapPinIcon class="h-4 w-4 mr-2 text-green-500" />
                          <span class="font-medium px-3 py-2 bg-green-100 text-green-800 rounded-lg">
                            📍 {{ event.location }}
                          </span>
                        </div>
                      </div>

                      <!-- Description -->
                      <div v-if="event.description" class="text-sm text-gray-600">
                        <div class="flex items-start">
                          <DocumentTextIcon class="h-4 w-4 mr-2 mt-0.5 text-gray-400" />
                          <div>
                            <div class="font-medium text-gray-700 mb-1">描述</div>
                            <p class="whitespace-pre-wrap">{{ event.description }}</p>
                          </div>
                        </div>
                      </div>

                      <!-- Event Duration -->
                      <div class="flex items-center text-sm text-gray-500">
                        <span class="font-medium mr-2">时长:</span>
                        <span>{{ eventDuration }}</span>
                      </div>

                      <!-- Created/Updated Time -->
                      <div class="text-xs text-gray-400 border-t pt-3">
                        <div>创建时间: {{ formatDisplayDateTime(event.created_at) }}</div>
                        <div v-if="event.updated_at !== event.created_at">
                          更新时间: {{ formatDisplayDateTime(event.updated_at) }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  @click="$emit('close')"
                  class="inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:ml-3 sm:w-auto"
                >
                  关闭
                </button>
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
  UserIcon,
  DocumentTextIcon,
  AcademicCapIcon,
  CalendarDaysIcon,
  BookmarkIcon,
} from '@heroicons/vue/24/outline';
import { formatDisplayDateTime } from '@/utils/date';
import { getUserColor } from '@/utils/colors';
import type { Event } from '@/types';

interface Props {
  isOpen: boolean;
  event?: Event | null;
}

const props = defineProps<Props>();

defineEmits<{
  close: [];
}>();

const eventColor = computed(() => {
  if (!props.event) return { bg: '#f3f4f6', text: '#374151' };
  // 使用 owner?.id 而不是 owner_id，并提供默认值
  const userId = props.event.owner?.id || props.event.schedule_id || 0;
  return getUserColor(userId);
});

const eventDuration = computed(() => {
  if (!props.event) return '';
  
  const start = new Date(props.event.start_time);
  const end = new Date(props.event.end_time);
  const diffMs = end.getTime() - start.getTime();
  
  const hours = Math.floor(diffMs / (1000 * 60 * 60));
  const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
  
  if (hours === 0) {
    return `${minutes}分钟`;
  } else if (minutes === 0) {
    return `${hours}小时`;
  } else {
    return `${hours}小时${minutes}分钟`;
  }
});

// 获取星期几的中文显示
function getDayOfWeekText(dayOfWeek: number): string {
  const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
  return days[dayOfWeek] || '未知';
}
</script>
