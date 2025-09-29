<template>
  <div class="h-full flex flex-col bg-gray-50">
    <!-- Header -->
    <div class="px-4 py-3 border-b border-gray-200 bg-white">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-900">课表管理</h2>
        <button
          @click="openCreateModal"
          class="inline-flex items-center gap-x-1.5 rounded-md bg-primary-600 px-2.5 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
        >
          <PlusIcon class="h-4 w-4" />
          新建
        </button>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="scheduleStore.isLoading" class="flex-1 flex items-center justify-center">
      <div class="h-6 w-6 animate-spin rounded-full border-2 border-primary-600 border-t-transparent"></div>
    </div>

    <!-- Error state -->
    <div v-else-if="scheduleStore.error" class="px-4 py-3">
      <div class="rounded-md bg-red-50 p-3">
        <div class="flex">
          <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
          <div class="ml-3">
            <p class="text-sm text-red-800">{{ scheduleStore.error }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Schedule list -->
    <div v-else class="flex-1 overflow-y-auto">
      <div class="px-2 py-3 space-y-1">
        <div
          v-for="schedule in scheduleStore.schedules"
          :key="schedule.id"
          @click="selectSchedule(schedule.id)"
          :class="[
            'group relative flex items-center justify-between rounded-md px-3 py-2 cursor-pointer transition-colors',
            schedule.id === scheduleStore.activeScheduleId
              ? 'bg-primary-100 text-primary-900 ring-1 ring-primary-200'
              : 'text-gray-700 hover:bg-gray-100'
          ]"
        >
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <div 
                :class="[
                  'w-2 h-2 rounded-full flex-shrink-0',
                  schedule.status === '进行' ? 'bg-green-500' : 
                  schedule.status === '结束' ? 'bg-gray-400' : 'bg-yellow-500'
                ]"
              ></div>
              <p class="text-sm font-medium truncate">{{ schedule.name }}</p>
            </div>
            <p class="text-xs text-gray-500 mt-0.5">
              {{ formatScheduleInfo(schedule) }}
            </p>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <!-- Export button -->
            <button
              @click.stop="exportSchedule(schedule.id)"
              class="p-1.5 text-gray-400 hover:text-blue-600 rounded-md hover:bg-blue-50"
              title="导出ICS"
            >
              <ArrowDownTrayIcon class="h-4 w-4" />
            </button>
            
            <!-- Edit button -->
            <button
              @click.stop="openEditModal(schedule)"
              class="p-1.5 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100"
              title="编辑课表"
            >
              <PencilIcon class="h-4 w-4" />
            </button>
          </div>
        </div>

        <!-- Empty state -->
        <div v-if="scheduleStore.schedules.length === 0" class="px-3 py-8 text-center">
          <CalendarIcon class="mx-auto h-12 w-12 text-gray-400" />
          <h3 class="mt-2 text-sm font-medium text-gray-900">还没有课表</h3>
          <p class="mt-1 text-sm text-gray-500">
            创建您的第一个课表开始使用
          </p>
          <div class="mt-6">
            <button
              @click="openCreateModal"
              class="inline-flex items-center gap-x-1.5 rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500"
            >
              <PlusIcon class="h-4 w-4" />
              新建课表
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Active schedule summary -->
    <div v-if="scheduleStore.activeSchedule" class="border-t border-gray-200 bg-white px-4 py-3">
      <div class="text-xs text-gray-500">
        当前课表: <span class="font-medium text-gray-900">{{ scheduleStore.activeSchedule.name }}</span>
      </div>
      <div class="text-xs text-gray-500 mt-1">
        {{ scheduleStore.currentMyEvents?.length || 0 }} 个事件
      </div>
    </div>

    <!-- Schedule Editor Modal -->
    <ScheduleEditor
      :is-open="isEditorOpen"
      :schedule-data="selectedScheduleData"
      @close="closeEditor"
      @save="handleScheduleSave"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useScheduleStore } from '@/stores/schedule';
import ScheduleEditor from './ScheduleEditor.vue';
import {
  PlusIcon,
  PencilIcon,
  ArrowDownTrayIcon,
  ExclamationTriangleIcon,
  CalendarIcon,
} from '@heroicons/vue/24/outline';
import { formatDisplayDateShort } from '@/utils/date';
import type { ScheduleResponse } from '@/types';

const scheduleStore = useScheduleStore();

const isEditorOpen = ref(false);
const selectedScheduleData = ref<ScheduleResponse | null>(null);

// Methods
function selectSchedule(scheduleId: number) {
  scheduleStore.setActiveSchedule(scheduleId);
}

function openCreateModal() {
  selectedScheduleData.value = null;
  isEditorOpen.value = true;
}

function openEditModal(schedule: ScheduleResponse) {
  selectedScheduleData.value = schedule;
  isEditorOpen.value = true;
}

function closeEditor() {
  isEditorOpen.value = false;
  selectedScheduleData.value = null;
}

async function handleScheduleSave() {
  await scheduleStore.fetchSchedules();
  closeEditor();
}

async function exportSchedule(scheduleId: number) {
  try {
    // Temporarily set active schedule to export the correct one
    const originalActiveId = scheduleStore.activeScheduleId;
    scheduleStore.setActiveSchedule(scheduleId);
    
    await scheduleStore.exportSchedule();
    
    // Restore original active schedule
    if (originalActiveId !== scheduleId) {
      scheduleStore.setActiveSchedule(originalActiveId);
    }
  } catch (error) {
    console.error('Failed to export schedule:', error);
  }
}

function formatScheduleInfo(schedule: ScheduleResponse): string {
  const parts = [];
  
  if (schedule.total_weeks) {
    parts.push(`${schedule.total_weeks}周`);
  }
  
  if (schedule.start_date) {
    const startDate = new Date(schedule.start_date);
    parts.push(`从 ${formatDisplayDateShort(schedule.start_date)}`);
  }
  
  return parts.join(' • ') || '无信息';
}
</script>
