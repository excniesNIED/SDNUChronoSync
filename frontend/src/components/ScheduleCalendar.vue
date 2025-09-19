<template>
  <div class="calendar-container">
    <!-- Week view -->
    <div v-if="viewMode === 'week'" class="week-view">
      <!-- Header -->
      <div class="grid grid-cols-8 border-b border-gray-200">
        <div class="p-4"></div>
        <div
          v-for="day in weekDays"
          :key="day.toISOString()"
          class="p-4 text-center"
        >
          <div class="text-sm font-medium text-gray-900">
            {{ formatDayHeader(day) }}
          </div>
          <div
            :class="[
              'text-2xl font-semibold mt-1',
              isToday(day) ? 'text-primary-600' : 'text-gray-700'
            ]"
          >
            {{ day.getDate() }}
          </div>
        </div>
      </div>

      <!-- Time slots -->
      <div class="grid grid-cols-8">
        <!-- Time column -->
        <div class="border-r border-gray-200">
          <div
            v-for="hour in timeSlots"
            :key="hour"
            class="h-16 border-b border-gray-100 flex items-center justify-center text-xs text-gray-500"
          >
            {{ formatTimeSlot(hour) }}
          </div>
        </div>

        <!-- Day columns -->
        <div
          v-for="day in weekDays"
          :key="day.toISOString()"
          class="relative border-r border-gray-200 last:border-r-0"
        >
          <!-- Time slots background -->
          <div
            v-for="hour in timeSlots"
            :key="hour"
            class="h-16 border-b border-gray-100 cursor-pointer hover:bg-gray-50"
            @click="$emit('date-click', new Date(day.getFullYear(), day.getMonth(), day.getDate(), hour))"
          ></div>

          <!-- Events -->
          <div
            v-for="event in getDayEvents(day)"
            :key="event.id"
            :style="getEventStyle(event)"
            class="absolute left-1 right-1 rounded-md px-2 py-1 text-xs cursor-pointer shadow-sm hover:shadow-md transition-shadow z-10"
            @click="$emit('event-click', event)"
          >
            <div class="font-medium truncate">{{ event.title }}</div>
            <div class="text-xs opacity-75 truncate">
              {{ formatTime(event.start_time) }} - {{ formatTime(event.end_time) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Month view -->
    <div v-else class="month-view">
      <!-- Month header -->
      <div class="grid grid-cols-7 border-b border-gray-200">
        <div
          v-for="day in ['日', '一', '二', '三', '四', '五', '六']"
          :key="day"
          class="p-4 text-center text-sm font-medium text-gray-900"
        >
          {{ day }}
        </div>
      </div>

      <!-- Calendar grid -->
      <div class="grid grid-cols-7">
        <div
          v-for="day in monthDays"
          :key="day.toISOString()"
          :class="[
            'min-h-[120px] border-b border-r border-gray-200 last:border-r-0 p-2 cursor-pointer hover:bg-gray-50',
            !isSameMonth(day, currentDate) ? 'bg-gray-50 text-gray-400' : 'bg-white',
          ]"
          @click="$emit('date-click', day)"
        >
          <div
            :class="[
              'text-sm font-medium mb-1',
              isToday(day) ? 'bg-primary-600 text-white rounded-full w-6 h-6 flex items-center justify-center' : ''
            ]"
          >
            {{ day.getDate() }}
          </div>

          <!-- Events -->
          <div class="space-y-1">
            <div
              v-for="event in getDayEvents(day).slice(0, 3)"
              :key="event.id"
              :style="{ backgroundColor: event.color, color: event.textColor }"
              class="text-xs px-2 py-1 rounded truncate cursor-pointer hover:shadow-sm"
              @click.stop="$emit('event-click', event)"
            >
              {{ event.title }}
            </div>
            <div
              v-if="getDayEvents(day).length > 3"
              class="text-xs text-gray-500 px-2"
            >
              +{{ getDayEvents(day).length - 3 }} 更多
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { CalendarEvent } from '@/types';
import {
  formatDisplayTime,
  getWeekDays,
  getCalendarDays,
  isToday,
  isSameDay,
  addDays
} from '@/utils/date';

interface Props {
  events: CalendarEvent[];
  viewMode: 'week' | 'month';
  currentDate: Date;
}

const props = defineProps<Props>();

defineEmits<{
  'event-click': [event: CalendarEvent];
  'date-click': [date: Date];
}>();

// Time slots for week view (8 AM to 8 PM)
const timeSlots = Array.from({ length: 12 }, (_, i) => i + 8);

const weekDays = computed(() => {
  return getWeekDays(props.currentDate);
});

const monthDays = computed(() => {
  return getCalendarDays(props.currentDate);
});

function formatDayHeader(date: Date): string {
  const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
  return days[date.getDay()];
}

function formatTimeSlot(hour: number): string {
  return `${hour.toString().padStart(2, '0')}:00`;
}

function formatTime(dateTime: string): string {
  return formatDisplayTime(new Date(dateTime));
}

function isSameMonth(date1: Date, date2: Date): boolean {
  return date1.getFullYear() === date2.getFullYear() && 
         date1.getMonth() === date2.getMonth();
}

function getDayEvents(day: Date): CalendarEvent[] {
  return props.events.filter(event => {
    const eventDate = new Date(event.start_time);
    return isSameDay(eventDate, day);
  }).sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());
}

function getEventStyle(event: CalendarEvent) {
  const startTime = new Date(event.start_time);
  const endTime = new Date(event.end_time);
  
  // Calculate position and height for week view
  const startHour = startTime.getHours() + startTime.getMinutes() / 60;
  const endHour = endTime.getHours() + endTime.getMinutes() / 60;
  
  // Only show events within our time range (8 AM to 8 PM)
  const displayStartHour = Math.max(8, startHour);
  const displayEndHour = Math.min(20, endHour);
  
  const top = ((displayStartHour - 8) / 12) * 100;
  const height = ((displayEndHour - displayStartHour) / 12) * 100;
  
  return {
    top: `${top}%`,
    height: `${Math.max(height, 8)}%`, // Minimum height
    backgroundColor: event.color,
    color: event.textColor,
    borderLeft: `3px solid ${event.textColor}`,
  };
}
</script>

<style scoped>
.calendar-container {
  @apply w-full overflow-hidden;
}

.week-view {
  @apply min-h-[600px];
}

.month-view {
  @apply min-h-[600px];
}
</style>
