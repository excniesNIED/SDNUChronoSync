<template>
  <div class="space-y-6">
    <!-- Action bar -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div class="flex items-center gap-4">
        <!-- View mode toggle -->
        <div class="flex rounded-md shadow-sm">
          <button
            @click="setViewMode('week')"
            :class="[
              viewMode === 'week'
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50',
              'relative inline-flex items-center rounded-l-md px-3 py-2 text-sm font-semibold ring-1 ring-inset ring-gray-300 focus:z-10'
            ]"
          >
            周视图
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
            月视图
          </button>
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

      <div class="flex items-center gap-3">
        <!-- Import button -->
        <button
          @click="openImportModal"
          class="inline-flex items-center gap-x-2 rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
        >
          <CloudArrowDownIcon class="h-4 w-4" />
          从教务系统导入
        </button>

        <!-- Export button -->
        <button
          @click="exportSchedule"
          class="inline-flex items-center gap-x-2 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
        >
          <ArrowDownTrayIcon class="h-4 w-4" />
          导出
        </button>

        <!-- Add event button -->
        <button
          @click="openCreateModal"
          class="inline-flex items-center gap-x-2 rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
        >
          <PlusIcon class="h-4 w-4" />
          添加日程
        </button>
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
      @close="closeImportModal"
      @success="handleImportSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useScheduleStore } from '@/stores/schedule';
import ScheduleCalendar from './ScheduleCalendar.vue';
import EventModal from './EventModal.vue';
import ScheduleImporter from './ScheduleImporter.vue';
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  PlusIcon,
  ArrowDownTrayIcon,
  CloudArrowDownIcon,
  ExclamationTriangleIcon,
} from '@heroicons/vue/24/outline';
import { formatDisplayDate, formatDisplayDateTime, addWeeks, addMonths } from '@/utils/date';
import { getUserColor } from '@/utils/colors';
import type { Event, CalendarEvent } from '@/types';

const authStore = useAuthStore();
const scheduleStore = useScheduleStore();

const currentDate = ref(new Date());
const viewMode = ref<'week' | 'month'>('week');
const isModalOpen = ref(false);
const isImportModalOpen = ref(false);
const selectedEvent = ref<Event | null>(null);

// Computed properties
const currentDateTitle = computed(() => {
  if (viewMode.value === 'week') {
    return `${formatDisplayDate(currentDate.value)} 周`;
  } else {
    return `${currentDate.value.getFullYear()}年${currentDate.value.getMonth() + 1}月`;
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
  // 重新获取课表数据
  await scheduleStore.fetchMyEvents();
  closeImportModal();
}

function handleEventClick(event: Event) {
  selectedEvent.value = event;
  isModalOpen.value = true;
}

function handleDateClick(date: Date) {
  // Create new event at clicked date
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

async function exportSchedule() {
  await scheduleStore.exportSchedule();
}

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
