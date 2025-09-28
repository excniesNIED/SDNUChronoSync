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
            v-for="(timeSlot, index) in timeSlots"
            :key="index"
            class="h-24 border-b border-gray-100 flex items-center justify-center text-xs text-gray-500"
          >
            <div class="text-center">
              <div class="font-medium">{{ timeSlot.period }}</div>
              <div class="text-xs opacity-75">{{ timeSlot.start }}-{{ timeSlot.end }}</div>
            </div>
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
            v-for="(timeSlot, index) in timeSlots"
            :key="index"
            class="h-24 border-b border-gray-100 cursor-pointer hover:bg-gray-50"
            @click="$emit('date-click', day)"
          ></div>

          <!-- Events -->
          <div
            v-for="(eventGroup, groupIndex) in getGroupedDayEvents(day)"
            :key="`group-${groupIndex}`"
            :style="getEventGroupStyle(eventGroup, groupIndex)"
            class="absolute left-1 right-1 z-10"
          >
            <!-- Multiple events in same time slot -->
            <div v-if="eventGroup.length > 1" class="space-y-1">
              <div
                v-for="event in eventGroup"
                :key="event.id"
                :style="{ backgroundColor: event.color, color: event.textColor }"
                class="rounded-md px-2 py-1 text-xs cursor-pointer shadow-sm hover:shadow-md transition-shadow"
                @click="$emit('event-click', event)"
              >
                <div class="font-medium truncate">{{ event.title }}</div>
                <div v-if="event.instructor" class="text-xs opacity-75 truncate">
                  {{ event.instructor }}
                </div>
                <div v-if="event.owner" class="text-xs opacity-60 truncate">
                  {{ event.owner.full_name }}
                </div>
                <!-- 团队视图中显示简化的周数和地址 -->
                <div v-if="props.isAdminMode && event.weeks_display" class="text-xs opacity-60 truncate">
                  {{ event.weeks_display }}
                </div>
                <div v-if="props.isAdminMode && event.location" class="text-xs opacity-60 truncate">
                  📍 {{ event.location }}
                </div>
              </div>
            </div>
            <!-- Single event -->
            <div
              v-else-if="eventGroup.length === 1"
              :style="{ backgroundColor: eventGroup[0].color, color: eventGroup[0].textColor }"
              class="rounded-md px-2 py-1 text-xs cursor-pointer shadow-sm hover:shadow-md transition-shadow h-full"
              @click="$emit('event-click', eventGroup[0])"
            >
              <div class="font-medium truncate">{{ eventGroup[0].title }}</div>
              <div v-if="eventGroup[0].instructor" class="text-xs opacity-75 truncate">
                {{ eventGroup[0].instructor }}
              </div>
              <div v-if="eventGroup[0].owner" class="text-xs opacity-60 truncate">
                {{ eventGroup[0].owner.full_name }}
              </div>
              <!-- 个人视图中显示周数和地址 -->
              <div v-if="!props.isAdminMode && eventGroup[0].weeks_display" class="text-xs opacity-70 truncate">
                {{ eventGroup[0].weeks_display }}
              </div>
              <div v-if="!props.isAdminMode && eventGroup[0].location" class="text-xs opacity-70 truncate">
                📍 {{ eventGroup[0].location }}
              </div>
              <div v-if="props.isAdminMode" class="text-xs opacity-75 truncate">
                {{ formatTime(eventGroup[0].start_time) }} - {{ formatTime(eventGroup[0].end_time) }}
              </div>
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
          v-for="day in ['一', '二', '三', '四', '五', '六', '日']"
          :key="day"
          class="p-4 text-center text-sm font-medium text-gray-900"
        >
          周{{ day }}
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
              class="text-xs px-2 py-1 rounded cursor-pointer hover:shadow-sm"
              @click.stop="$emit('event-click', event)"
            >
              <div class="truncate font-medium">{{ event.title }}</div>
              <div v-if="event.instructor" class="truncate text-xs opacity-80">
                {{ event.instructor }}
              </div>
              <!-- 个人视图中显示周数和地址 -->
              <div v-if="!props.isAdminMode && event.weeks_display" class="truncate text-xs opacity-70">
                {{ event.weeks_display }}
              </div>
              <div v-if="!props.isAdminMode && event.location" class="truncate text-xs opacity-70">
                📍 {{ event.location }}
              </div>
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
  getWeekStart,
  getCalendarDays,
  isToday,
  isSameDay,
  addDays
} from '@/utils/date';

interface Props {
  events: CalendarEvent[];
  viewMode: 'week' | 'month';
  currentDate: Date;
  isAdminMode?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  isAdminMode: false,
});

defineEmits<{
  'event-click': [event: CalendarEvent];
  'date-click': [date: Date];
}>();

// 课表时间段（按照山东师范大学作息时间）
const classTimeSlots = [
  { period: '第1节', start: '08:20', end: '09:05' },
  { period: '第2节', start: '09:10', end: '09:55' },
  { period: '第3节', start: '10:10', end: '10:55' },
  { period: '第4节', start: '11:00', end: '11:45' },
  { period: '第5节', start: '14:00', end: '14:45' },
  { period: '第6节', start: '14:50', end: '15:35' },
  { period: '第7节', start: '15:50', end: '16:35' },
  { period: '第8节', start: '16:40', end: '17:25' },
  { period: '第9节', start: '19:00', end: '19:45' },
  { period: '第10节', start: '19:45', end: '20:30' }
];

const timeSlots = classTimeSlots;

const weekDays = computed(() => {
  // 确保周视图从星期一开始
  const weekStart = getWeekStart(props.currentDate);
  return getWeekDays(weekStart);
});

const monthDays = computed(() => {
  return getCalendarDays(props.currentDate);
});

function formatDayHeader(date: Date): string {
  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
  // 调整索引：星期一(1)对应索引0，星期日(0)对应索引6
  const dayIndex = date.getDay() === 0 ? 6 : date.getDay() - 1;
  return days[dayIndex];
}

function formatTimeSlot(timeSlot: any): string {
  if (typeof timeSlot === 'object') {
    return timeSlot.period;
  }
  return `${timeSlot.toString().padStart(2, '0')}:00`;
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

// 新增：将同一天的事件按时间段分组
function getGroupedDayEvents(day: Date): CalendarEvent[][] {
  const dayEvents = getDayEvents(day);
  const groups: Map<string, CalendarEvent[]> = new Map();

  dayEvents.forEach(event => {
    const startTime = new Date(event.start_time);
    const endTime = new Date(event.end_time);
    
    // 创建时间段标识符
    const timeKey = `${startTime.getHours()}:${startTime.getMinutes()}-${endTime.getHours()}:${endTime.getMinutes()}`;
    
    if (!groups.has(timeKey)) {
      groups.set(timeKey, []);
    }
    groups.get(timeKey)!.push(event);
  });

  // 按时间顺序返回分组
  return Array.from(groups.values()).sort((a, b) => {
    const aStart = new Date(a[0].start_time).getTime();
    const bStart = new Date(b[0].start_time).getTime();
    return aStart - bStart;
  });
}

function getEventStyle(event: CalendarEvent) {
  const startTime = new Date(event.start_time);
  const endTime = new Date(event.end_time);
  
  // 获取时间对应的时间段索引
  const startTimeStr = `${startTime.getHours().toString().padStart(2, '0')}:${startTime.getMinutes().toString().padStart(2, '0')}`;
  const endTimeStr = `${endTime.getHours().toString().padStart(2, '0')}:${endTime.getMinutes().toString().padStart(2, '0')}`;
  
  // 查找事件所在的时间段
  let timeSlotIndex = -1;
  let timeSlotHeight = 1;
  
  for (let i = 0; i < timeSlots.length; i++) {
    const slot = timeSlots[i];
    if (startTimeStr >= slot.start && startTimeStr < slot.end) {
      timeSlotIndex = i;
      // 计算跨越的时间段数量
      for (let j = i; j < timeSlots.length; j++) {
        if (endTimeStr <= timeSlots[j].end) {
          timeSlotHeight = j - i + 1;
          break;
        }
      }
      break;
    }
  }
  
  // 如果找不到匹配的时间段，默认显示在第一个时间段
  if (timeSlotIndex === -1) {
    timeSlotIndex = 0;
    timeSlotHeight = 1;
  }
  
  const top = (timeSlotIndex / timeSlots.length) * 100;
  const height = (timeSlotHeight / timeSlots.length) * 100;
  
  return {
    top: `${top}%`,
    height: `${Math.max(height, 14)}%`, // Minimum height
    backgroundColor: event.color,
    color: event.textColor,
    borderLeft: `3px solid ${event.textColor}`,
  };
}

// 新增：获取事件组的样式
function getEventGroupStyle(eventGroup: CalendarEvent[], groupIndex: number) {
  if (eventGroup.length === 0) return {};
  
  // 使用第一个事件的时间来计算位置
  const firstEvent = eventGroup[0];
  const startTime = new Date(firstEvent.start_time);
  const endTime = new Date(firstEvent.end_time);
  
  // 获取时间对应的时间段索引
  const startTimeStr = `${startTime.getHours().toString().padStart(2, '0')}:${startTime.getMinutes().toString().padStart(2, '0')}`;
  const endTimeStr = `${endTime.getHours().toString().padStart(2, '0')}:${endTime.getMinutes().toString().padStart(2, '0')}`;
  
  let timeSlotIndex = -1;
  let timeSlotHeight = 1;
  
  for (let i = 0; i < timeSlots.length; i++) {
    const slot = timeSlots[i];
    if (startTimeStr >= slot.start && startTimeStr < slot.end) {
      timeSlotIndex = i;
      for (let j = i; j < timeSlots.length; j++) {
        if (endTimeStr <= timeSlots[j].end) {
          timeSlotHeight = j - i + 1;
          break;
        }
      }
      break;
    }
  }
  
  if (timeSlotIndex === -1) {
    timeSlotIndex = 0;
    timeSlotHeight = 1;
  }
  
  const top = (timeSlotIndex / timeSlots.length) * 100;
  const height = (timeSlotHeight / timeSlots.length) * 100;
  
  return {
    top: `${top}%`,
    height: `${Math.max(height, 14)}%`,
  };
}
</script>

<style scoped>
.calendar-container {
  @apply w-full overflow-hidden;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 80vh;
  padding: 1rem;
}

.week-view, .month-view {
  @apply min-h-[800px] w-full max-w-7xl;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border-radius: 0.5rem;
  background: white;
}

.week-view {
  /* 确保晚上课程有足够空间显示 */
  min-height: 900px;
}
</style>
