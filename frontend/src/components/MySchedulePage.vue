<template>
  <div class="space-y-6">
    <!-- Header with schedule selector -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <!-- Mobile layout (3 rows for < 640px) -->
      <div class="sm:hidden space-y-4">
        <!-- Row 1: Schedule selector -->
        <div class="flex items-center">
          <div class="relative flex-1">
            <Menu as="div" class="relative inline-block text-left w-full">
              <div>
                <MenuButton class="inline-flex w-full justify-center gap-x-1.5 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                  <CalendarIcon class="h-5 w-5 text-gray-400" />
                  {{ scheduleStore.activeSchedule?.name || '选择课表' }}
                  <ChevronDownIcon class="-mr-1 h-5 w-5 text-gray-400" />
                </MenuButton>
              </div>
              <!-- Schedule dropdown content same as before -->
              <transition
                enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <MenuItems class="absolute left-0 z-10 mt-2 w-80 origin-top-left divide-y divide-gray-100 rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                  <div class="px-4 py-3">
                    <p class="text-sm font-medium text-gray-900">我的课表</p>
                  </div>
                  <div class="py-1">
                    <MenuItem
                      v-for="schedule in scheduleStore.schedules"
                      :key="schedule.id"
                      v-slot="{ active }"
                    >
                      <div
                        @click="selectSchedule(schedule.id)"
                        :class="[
                          active ? 'bg-gray-100' : '',
                          'group flex items-center justify-between px-4 py-2 text-sm cursor-pointer'
                        ]"
                      >
                        <div class="flex items-center gap-3">
                          <div 
                            :class="[
                              'w-2 h-2 rounded-full flex-shrink-0',
                              schedule.status === '进行' ? 'bg-green-500' : 
                              schedule.status === '结束' ? 'bg-gray-400' : 'bg-yellow-500'
                            ]"
                          ></div>
                          <div>
                            <p class="font-medium text-gray-900">{{ schedule.name }}</p>
                            <p class="text-xs text-gray-500">{{ formatScheduleInfo(schedule) }}</p>
                          </div>
                        </div>
                        <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100">
                          <button
                            @click.stop="exportSchedule(schedule.id)"
                            class="p-1 text-gray-400 hover:text-blue-600 rounded"
                            title="导出"
                          >
                            <ArrowDownTrayIcon class="h-4 w-4" />
                          </button>
                          <button
                            @click.stop="openEditScheduleModal(schedule)"
                            class="p-1 text-gray-400 hover:text-gray-600 rounded"
                            title="编辑"
                          >
                            <PencilIcon class="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </MenuItem>
                  </div>
                  <div class="py-1">
                    <MenuItem v-slot="{ active }">
                      <button
                        @click="openCreateScheduleModal"
                        :class="[
                          active ? 'bg-gray-100' : '',
                          'group flex w-full items-center px-4 py-2 text-sm text-gray-700'
                        ]"
                      >
                        <PlusIcon class="mr-3 h-4 w-4 text-gray-400 group-hover:text-gray-500" />
                        新建课表
                      </button>
                    </MenuItem>
                  </div>
                </MenuItems>
              </transition>
            </Menu>
          </div>
        </div>

        <!-- Row 2: View mode and navigation buttons -->
        <div class="flex items-center justify-between">
          <!-- View mode dropdown for mobile -->
          <div class="flex items-center gap-3">
            <Menu as="div" class="relative inline-block text-left">
              <div>
                <MenuButton class="inline-flex w-full justify-center gap-x-1.5 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                  {{ viewMode === 'week' ? '周' : '月' }}
                  <ChevronDownIcon class="-mr-1 h-5 w-5 text-gray-400" />
                </MenuButton>
              </div>
              <transition
                enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <MenuItems class="absolute left-0 z-10 mt-2 w-32 origin-top-left rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                  <div class="py-1">
                    <MenuItem v-slot="{ active }">
                      <button
                        @click="setViewMode('week')"
                        :class="[
                          active ? 'bg-gray-100' : '',
                          viewMode === 'week' ? 'font-semibold' : '',
                          'group flex w-full items-center px-4 py-2 text-sm text-gray-700'
                        ]"
                      >
                        周视图
                      </button>
                    </MenuItem>
                    <MenuItem v-slot="{ active }">
                      <button
                        @click="setViewMode('month')"
                        :class="[
                          active ? 'bg-gray-100' : '',
                          viewMode === 'month' ? 'font-semibold' : '',
                          'group flex w-full items-center px-4 py-2 text-sm text-gray-700'
                        ]"
                      >
                        月视图
                      </button>
                    </MenuItem>
                  </div>
                </MenuItems>
              </transition>
            </Menu>

            <!-- Navigation buttons -->
            <button
              v-if="scheduleStore.activeSchedule?.start_date"
              @click="jumpToScheduleStart"
              class="px-3 py-1.5 text-xs bg-blue-100 text-blue-700 hover:bg-blue-200 rounded-md transition-colors"
              title="跳转到开学时间"
            >
              开学
            </button>
            
            <button
              @click="jumpToToday"
              class="px-3 py-1.5 text-xs bg-green-100 text-green-700 hover:bg-green-200 rounded-md transition-colors"
              title="跳转到今天"
            >
              今天
            </button>
            
            <button
              @click="forceRefreshEvents"
              class="px-3 py-1.5 text-xs bg-yellow-100 text-yellow-700 hover:bg-yellow-200 rounded-md transition-colors"
              title="强制刷新课程数据"
            >
              刷新
            </button>
          </div>

          <!-- Date navigation for mobile -->
          <div class="flex items-center gap-2">
            <button
              @click="navigateDate(-1)"
              class="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100"
            >
              <ChevronLeftIcon class="h-5 w-5" />
            </button>
            <h2 class="text-sm font-semibold text-gray-900 min-w-[120px] text-center">
              {{ currentDateTitle }}
            </h2>
            <button
              @click="navigateDate(1)"
              class="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100"
            >
              <ChevronRightIcon class="h-5 w-5" />
            </button>
          </div>
        </div>

        <!-- Row 3: Action buttons (icons only for mobile) -->
        <div class="flex items-center justify-center gap-4">
          <!-- Schedule Adjustment button -->
          <button
            v-if="scheduleStore.activeSchedule"
            @click="openAdjustmentModal"
            class="inline-flex items-center justify-center w-10 h-10 rounded-md bg-yellow-600 text-white shadow-sm hover:bg-yellow-500"
            title="调休"
          >
            <CalendarDaysIcon class="h-5 w-5" />
          </button>

          <!-- Import button -->
          <button
            @click="openImportModal"
            class="inline-flex items-center justify-center w-10 h-10 rounded-md bg-blue-600 text-white shadow-sm hover:bg-blue-500"
            title="导入"
          >
            <CloudArrowDownIcon class="h-5 w-5" />
          </button>

          <!-- Add event button -->
          <button
            @click="openCreateModal"
            class="inline-flex items-center justify-center w-10 h-10 rounded-md bg-primary-600 text-white shadow-sm hover:bg-primary-500"
            title="添加"
          >
            <PlusIcon class="h-5 w-5" />
          </button>
        </div>
      </div>

      <!-- Desktop layout (>= 640px) -->
      <div class="hidden sm:flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <!-- Top row for medium screens, left side for large screens -->
        <div class="flex flex-col lg:flex-row lg:items-center gap-4">
          <!-- Schedule selector -->
          <div class="relative">
            <Menu as="div" class="relative inline-block text-left">
              <div>
                <MenuButton class="inline-flex w-full justify-center gap-x-1.5 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                  <CalendarIcon class="h-5 w-5 text-gray-400" />
                  {{ scheduleStore.activeSchedule?.name || '选择课表' }}
                  <ChevronDownIcon class="-mr-1 h-5 w-5 text-gray-400" />
                </MenuButton>
              </div>
              <!-- Same dropdown content as mobile -->
              <transition
                enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <MenuItems class="absolute left-0 z-10 mt-2 w-80 origin-top-left divide-y divide-gray-100 rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                  <div class="px-4 py-3">
                    <p class="text-sm font-medium text-gray-900">我的课表</p>
                  </div>
                  <div class="py-1">
                    <MenuItem
                      v-for="schedule in scheduleStore.schedules"
                      :key="schedule.id"
                      v-slot="{ active }"
                    >
                      <div
                        @click="selectSchedule(schedule.id)"
                        :class="[
                          active ? 'bg-gray-100' : '',
                          'group flex items-center justify-between px-4 py-2 text-sm cursor-pointer'
                        ]"
                      >
                        <div class="flex items-center gap-3">
                          <div 
                            :class="[
                              'w-2 h-2 rounded-full flex-shrink-0',
                              schedule.status === '进行' ? 'bg-green-500' : 
                              schedule.status === '结束' ? 'bg-gray-400' : 'bg-yellow-500'
                            ]"
                          ></div>
                          <div>
                            <p class="font-medium text-gray-900">{{ schedule.name }}</p>
                            <p class="text-xs text-gray-500">{{ formatScheduleInfo(schedule) }}</p>
                          </div>
                        </div>
                        <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100">
                          <button
                            @click.stop="exportSchedule(schedule.id)"
                            class="p-1 text-gray-400 hover:text-blue-600 rounded"
                            title="导出"
                          >
                            <ArrowDownTrayIcon class="h-4 w-4" />
                          </button>
                          <button
                            @click.stop="openEditScheduleModal(schedule)"
                            class="p-1 text-gray-400 hover:text-gray-600 rounded"
                            title="编辑"
                          >
                            <PencilIcon class="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </MenuItem>
                  </div>
                  <div class="py-1">
                    <MenuItem v-slot="{ active }">
                      <button
                        @click="openCreateScheduleModal"
                        :class="[
                          active ? 'bg-gray-100' : '',
                          'group flex w-full items-center px-4 py-2 text-sm text-gray-700'
                        ]"
                      >
                        <PlusIcon class="mr-3 h-4 w-4 text-gray-400 group-hover:text-gray-500" />
                        新建课表
                      </button>
                    </MenuItem>
                  </div>
                </MenuItems>
              </transition>
            </Menu>
          </div>

          <!-- Date navigation -->
          <div class="flex items-center gap-2">
            <button
              @click="navigateDate(-1)"
              class="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100"
            >
              <ChevronLeftIcon class="h-5 w-5" />
            </button>
            <h2 class="text-lg font-semibold text-gray-900 min-w-[200px] text-center">
              {{ currentDateTitle }}
            </h2>
            <button
              @click="navigateDate(1)"
              class="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100"
            >
              <ChevronRightIcon class="h-5 w-5" />
            </button>
          </div>
        </div>

        <!-- Bottom row for medium screens, right side for large screens -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between lg:justify-end gap-4">
          <!-- View mode toggle and navigation buttons -->
          <div class="flex items-center gap-4">
            <!-- View mode toggle (button style for larger screens, dropdown for smaller) -->
            <div class="hidden lg:flex rounded-md shadow-sm">
              <button
                @click="setViewMode('week')"
                :class="[
                  viewMode === 'week'
                    ? 'bg-primary-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50',
                  'relative inline-flex items-center rounded-l-md px-3 py-2 text-sm font-semibold ring-1 ring-inset ring-gray-300 focus:z-10'
                ]"
              >
                <span class="hidden xl:inline">周视图</span>
                <span class="xl:hidden">周</span>
              </button>
              <button
                @click="setViewMode('month')"
                :class="[
                  viewMode === 'month'
                    ? 'bg-primary-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50',
                  'relative -ml-px inline-flex items-center rounded-r-md px-3 py-2 text-sm font-semibold ring-1 ring-inset ring-gray-300 focus:z-10'
                ]"
              >
                <span class="hidden xl:inline">月视图</span>
                <span class="xl:hidden">月</span>
              </button>
            </div>

            <!-- View mode dropdown for medium screens -->
            <div class="lg:hidden">
              <Menu as="div" class="relative inline-block text-left">
                <div>
                  <MenuButton class="inline-flex w-full justify-center gap-x-1.5 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                    {{ viewMode === 'week' ? '周' : '月' }}
                    <ChevronDownIcon class="-mr-1 h-5 w-5 text-gray-400" />
                  </MenuButton>
                </div>
                <transition
                  enter-active-class="transition ease-out duration-100"
                  enter-from-class="transform opacity-0 scale-95"
                  enter-to-class="transform opacity-100 scale-100"
                  leave-active-class="transition ease-in duration-75"
                  leave-from-class="transform opacity-100 scale-100"
                  leave-to-class="transform opacity-0 scale-95"
                >
                  <MenuItems class="absolute left-0 z-10 mt-2 w-32 origin-top-left rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                    <div class="py-1">
                      <MenuItem v-slot="{ active }">
                        <button
                          @click="setViewMode('week')"
                          :class="[
                            active ? 'bg-gray-100' : '',
                            viewMode === 'week' ? 'font-semibold' : '',
                            'group flex w-full items-center px-4 py-2 text-sm text-gray-700'
                          ]"
                        >
                          周视图
                        </button>
                      </MenuItem>
                      <MenuItem v-slot="{ active }">
                        <button
                          @click="setViewMode('month')"
                          :class="[
                            active ? 'bg-gray-100' : '',
                            viewMode === 'month' ? 'font-semibold' : '',
                            'group flex w-full items-center px-4 py-2 text-sm text-gray-700'
                          ]"
                        >
                          月视图
                        </button>
                      </MenuItem>
                    </div>
                  </MenuItems>
                </transition>
              </Menu>
            </div>

            <!-- Navigation buttons -->
            <div class="flex items-center gap-2">
              <button
                v-if="scheduleStore.activeSchedule?.start_date"
                @click="jumpToScheduleStart"
                class="px-3 py-1.5 text-xs bg-blue-100 text-blue-700 hover:bg-blue-200 rounded-md transition-colors"
                title="跳转到开学时间"
              >
                <span class="hidden xl:inline">开学</span>
                <span class="xl:hidden">开学</span>
              </button>
              
              <button
                @click="jumpToToday"
                class="px-3 py-1.5 text-xs bg-green-100 text-green-700 hover:bg-green-200 rounded-md transition-colors"
                title="跳转到今天"
              >
                <span class="hidden xl:inline">今天</span>
                <span class="xl:hidden">今天</span>
              </button>
              
              <button
                @click="forceRefreshEvents"
                class="px-3 py-1.5 text-xs bg-yellow-100 text-yellow-700 hover:bg-yellow-200 rounded-md transition-colors"
                title="强制刷新课程数据"
              >
                <span class="hidden xl:inline">刷新</span>
                <span class="xl:hidden">刷新</span>
              </button>
            </div>
          </div>

          <!-- Action buttons -->
          <div class="flex items-center gap-3">
            <!-- Schedule Adjustment button -->
            <button
              v-if="scheduleStore.activeSchedule"
              @click="openAdjustmentModal"
              class="inline-flex items-center gap-x-2 rounded-md bg-yellow-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-yellow-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-yellow-600"
              title="调休"
            >
              <CalendarDaysIcon class="h-4 w-4" />
              <span class="hidden 2xl:inline">调休</span>
            </button>

            <!-- Import button -->
            <button
              @click="openImportModal"
              class="inline-flex items-center gap-x-2 rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
              title="导入"
            >
              <CloudArrowDownIcon class="h-4 w-4" />
              <span class="hidden 2xl:inline">导入</span>
            </button>

            <!-- Add event button -->
            <button
              @click="openCreateModal"
              class="inline-flex items-center gap-x-2 rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
              title="添加"
            >
              <PlusIcon class="h-4 w-4" />
              <span class="hidden 2xl:inline">添加</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="scheduleStore.isLoading || scheduleStore.eventsLoading" class="flex justify-center py-12">
      <div class="h-8 w-8 animate-spin rounded-full border-2 border-primary-600 border-t-transparent"></div>
    </div>

    <!-- Error state -->
    <div v-else-if="scheduleStore.error || scheduleStore.eventsError" class="rounded-md bg-red-50 p-4">
      <div class="flex">
        <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">
            {{ scheduleStore.error || scheduleStore.eventsError }}
          </h3>
        </div>
      </div>
    </div>

    <!-- No active schedule warning -->
    <div v-else-if="!scheduleStore.activeSchedule" class="rounded-md bg-yellow-50 p-4">
      <div class="flex">
        <ExclamationTriangleIcon class="h-5 w-5 text-yellow-400" />
        <div class="ml-3">
          <h3 class="text-sm font-medium text-yellow-800">
            请创建或选择一个课表
          </h3>
          <p class="text-sm text-yellow-700 mt-1">
            您需要先创建一个课表才能查看和管理日程。
          </p>
        </div>
      </div>
    </div>

    <!-- Calendar -->
    <div v-else class="bg-white rounded-lg shadow">
      <ScheduleCalendar
        :events="calendarEvents"
        :view-mode="viewMode"
        :current-date="currentDate"
        :is-admin-mode="false"
        @event-click="handleEventClick"
        @date-click="handleDateClick"
      />
    </div>

    <!-- Event Modal -->
    <EventModal
      :is-open="isModalOpen"
      :event="selectedEvent"
      :is-admin="false"
      @close="closeModal"
      @save="handleEventSave"
      @delete="handleEventDelete"
    />

    <!-- Schedule Importer Modal -->
    <ScheduleImporter
      :is-open="isImportModalOpen"
      :current-schedule="scheduleStore.activeSchedule"
      @close="closeImportModal"
      @success="handleImportSuccess"
    />

    <!-- Schedule Editor Modal -->
    <ScheduleEditor
      :is-open="isScheduleEditorOpen"
      :schedule-data="selectedScheduleData"
      @close="closeScheduleEditor"
      @save="handleScheduleSave"
    />

    <!-- Schedule Adjuster Modal -->
    <ScheduleAdjuster
      :is-visible="isAdjustmentModalOpen"
      :schedule-id="scheduleStore.activeScheduleId || 0"
      @close="closeAdjustmentModal"
      @adjustment-applied="handleAdjustmentApplied"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue';
import { useAuthStore } from '@/stores/auth';
import { useScheduleStore } from '@/stores/schedule';
import ScheduleCalendar from './ScheduleCalendar.vue';
import EventModal from './EventModal.vue';
import ScheduleImporter from './ScheduleImporter.vue';
import ScheduleEditor from './ScheduleEditor.vue';
import ScheduleAdjuster from './ScheduleAdjuster.vue';
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  ChevronDownIcon,
  PlusIcon,
  ArrowDownTrayIcon,
  CloudArrowDownIcon,
  ExclamationTriangleIcon,
  CalendarIcon,
  CalendarDaysIcon,
  PencilIcon,
} from '@heroicons/vue/24/outline';
import { formatDisplayDate, formatDisplayDateTime, addWeeks, addMonths } from '@/utils/date';
import { getUserColor } from '@/utils/colors';
import type { Event, CalendarEvent, ScheduleResponse } from '@/types';

const authStore = useAuthStore();
const scheduleStore = useScheduleStore();

// 默认显示当前时间，如果有活跃课表且开学时间在未来，则显示开学时间
const currentDate = ref(new Date());
const viewMode = ref<'week' | 'month'>('week');
const isModalOpen = ref(false);
const isImportModalOpen = ref(false);
const isScheduleEditorOpen = ref(false);
const isAdjustmentModalOpen = ref(false);
const selectedEvent = ref<Event | null>(null);
const selectedScheduleData = ref<ScheduleResponse | null>(null);

// Computed properties
const currentDateTitle = computed(() => {
  if (viewMode.value === 'week') {
    return `${formatDisplayDate(currentDate.value)} 周`;
  } else {
    const year = currentDate.value.getFullYear();
    const month = String(currentDate.value.getMonth() + 1).padStart(2, '0');
    return `${year}年${month}月`;
  }
});

const calendarEvents = computed((): CalendarEvent[] => {
  if (!scheduleStore.currentMyEvents || scheduleStore.currentMyEvents.length === 0) {
    return [];
  }
  
  return scheduleStore.currentMyEvents.map(event => {
    const userColor = getUserColor(event.owner?.id || event.schedule_id);
    return {
      ...event,
      color: userColor.bg,
      textColor: userColor.text,
    };
  });
});

// Methods
function setViewMode(mode: 'week' | 'month') {
  viewMode.value = mode;
  scheduleStore.setViewMode({
    type: mode,
    date: currentDate.value,
  });
}

function navigateDate(direction: number) {
  if (viewMode.value === 'week') {
    currentDate.value = addWeeks(currentDate.value, direction);
  } else {
    currentDate.value = addMonths(currentDate.value, direction);
  }
  
  scheduleStore.setViewMode({
    type: viewMode.value,
    date: currentDate.value,
  });
}

function jumpToScheduleStart() {
  if (scheduleStore.activeSchedule?.start_date) {
    currentDate.value = new Date(scheduleStore.activeSchedule.start_date);
    console.log(`跳转到开学时间: ${formatDisplayDate(currentDate.value)}`);
    
    scheduleStore.setViewMode({
      type: viewMode.value,
      date: currentDate.value,
    });
  }
}

function jumpToToday() {
  currentDate.value = new Date();
  console.log(`跳转到今天: ${formatDisplayDate(currentDate.value)}`);
  
  scheduleStore.setViewMode({
    type: viewMode.value,
    date: currentDate.value,
  });
}

async function forceRefreshEvents() {
  if (!scheduleStore.activeScheduleId) {
    console.warn('没有活跃的课表');
    return;
  }
  
  try {
    console.log('强制刷新课程数据...');
    
    // 显示加载状态
    scheduleStore.eventsLoading = true;
    
    // 强制重新获取事件数据
    await scheduleStore.fetchMyEvents();
    
    console.log('课程数据刷新完成');
    
    // 可选：显示成功提示
    // 这里可以添加 toast 提示
    
  } catch (error) {
    console.error('刷新课程数据失败:', error);
    // 可选：显示错误提示
  } finally {
    scheduleStore.eventsLoading = false;
  }
}

function openCreateModal() {
  selectedEvent.value = null;
  isModalOpen.value = true;
}

function openImportModal() {
  isImportModalOpen.value = true;
}

function closeImportModal() {
  isImportModalOpen.value = false;
}

async function handleImportSuccess(count: number) {
  // 重新获取课表列表和事件数据
  await scheduleStore.fetchSchedules();
  closeImportModal();
}

function handleEventClick(event: Event, relatedEventsFromCalendar?: Event[]) {
  selectedEvent.value = event;
  isModalOpen.value = true;
}

function handleDateClick(date: Date) {
  if (!scheduleStore.activeSchedule) {
    console.warn('No active schedule found');
    return;
  }
  
  // 计算点击日期相对于课表开始日期的周数和星期几
  const scheduleStartDate = new Date(scheduleStore.activeSchedule.start_date);
  const clickedDate = new Date(date);
  
  // 计算天数差
  const daysDiff = Math.floor((clickedDate.getTime() - scheduleStartDate.getTime()) / (1000 * 60 * 60 * 24));
  
  // 计算周数（从第1周开始）
  const weekNumber = Math.floor(daysDiff / 7) + 1;
  
  // 计算星期几（1=周一, 7=周日）
  const dayOfWeek = clickedDate.getDay() === 0 ? 7 : clickedDate.getDay();
  
  // Create new event at clicked date with calculated week and day
  selectedEvent.value = {
    id: 0,
    schedule_id: scheduleStore.activeScheduleId || 0,
    title: '',
    description: '',
    location: '',
    start_time: formatDisplayDateTime(date),
    end_time: formatDisplayDateTime(new Date(date.getTime() + 60 * 60 * 1000)), // 1 hour later
    created_at: '',
    updated_at: '',
    day_of_week: dayOfWeek,
    weeks_input: weekNumber.toString(),
    weeks_display: `第${weekNumber}周`,
  };
  isModalOpen.value = true;
}

function closeModal() {
  isModalOpen.value = false;
  selectedEvent.value = null;
}

async function handleEventSave(eventData: any) {
  if (selectedEvent.value?.id) {
    // Update existing event
    await scheduleStore.updateEvent(selectedEvent.value.id, eventData);
  } else {
    // Create new event
    await scheduleStore.createEvent(eventData);
  }
  closeModal();
}

async function handleEventDelete(eventId: number) {
  await scheduleStore.deleteEvent(eventId);
  closeModal();
}

async function exportSchedule(scheduleId?: number) {
  if (scheduleId && scheduleId !== scheduleStore.activeScheduleId) {
    // Temporarily switch to export specific schedule
    const originalActiveId = scheduleStore.activeScheduleId;
    scheduleStore.setActiveSchedule(scheduleId);
    await scheduleStore.exportSchedule();
    if (originalActiveId) {
      scheduleStore.setActiveSchedule(originalActiveId);
    }
  } else {
    await scheduleStore.exportSchedule();
  }
}

// Schedule management methods
function selectSchedule(scheduleId: number) {
  scheduleStore.setActiveSchedule(scheduleId);
}

function openCreateScheduleModal() {
  selectedScheduleData.value = null;
  isScheduleEditorOpen.value = true;
}

function openEditScheduleModal(schedule: ScheduleResponse) {
  selectedScheduleData.value = schedule;
  isScheduleEditorOpen.value = true;
}

function closeScheduleEditor() {
  isScheduleEditorOpen.value = false;
  selectedScheduleData.value = null;
}

async function handleScheduleSave() {
  await scheduleStore.fetchSchedules();
  closeScheduleEditor();
}

function formatScheduleInfo(schedule: ScheduleResponse): string {
  const parts = [];
  
  if (schedule.total_weeks) {
    parts.push(`${schedule.total_weeks}周`);
  }
  
  if (schedule.start_date) {
    parts.push(`从 ${formatDisplayDate(schedule.start_date)}`);
  }
  
  return parts.join(' • ') || '无信息';
}

// Schedule adjustment methods
function openAdjustmentModal() {
  isAdjustmentModalOpen.value = true;
}

function closeAdjustmentModal() {
  isAdjustmentModalOpen.value = false;
}

async function handleAdjustmentApplied() {
  // 调休操作成功后，重新加载当前课表的事件数据
  if (scheduleStore.activeScheduleId) {
    await scheduleStore.fetchMyEvents();
  }
  closeAdjustmentModal();
}

// Watch for active schedule changes to update current date
watch(() => scheduleStore.activeSchedule, (newSchedule) => {
  if (newSchedule && newSchedule.start_date) {
    const scheduleStartDate = new Date(newSchedule.start_date);
    const now = new Date();
    
    // 如果课表开学时间比当前时间晚超过30天，则跳转到开学时间
    const daysDiff = (scheduleStartDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24);
    if (daysDiff > 30) {
      currentDate.value = scheduleStartDate;
      console.log(`跳转到课表开学时间: ${formatDisplayDate(scheduleStartDate)}`);
    }
  }
}, { immediate: true });

// Initialize
onMounted(async () => {
  // Check authentication
  await authStore.initialize();
  
  if (!authStore.isAuthenticated) {
    window.location.href = '/login';
    return;
  }

  // Load schedules first, which will auto-load events for active schedule
  await scheduleStore.fetchSchedules();
});
</script>
