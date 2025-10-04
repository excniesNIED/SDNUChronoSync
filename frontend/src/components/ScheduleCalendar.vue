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
          <div class="text-xs sm:text-sm font-medium text-gray-900">
            {{ formatDayHeader(day) }}
          </div>
          <div
            :class="[
              'text-xl sm:text-2xl font-semibold mt-1',
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
            @click="handleTimeSlotClick(day, index)"
          ></div>

          <!-- Events -->
          <div
            v-for="(eventGroup, groupIndex) in getGroupedDayEvents(day)"
            :key="`group-${groupIndex}`"
            :style="getEventGroupStyle(eventGroup, groupIndex)"
            class="absolute left-1 right-1 z-10"
          >
            <!-- Multiple events in same course (merged display) -->
            <div v-if="eventGroup.length > 1" class="space-y-1">
              <div
                :class="[
                  'rounded-md px-2 py-1 text-[11px] sm:text-xs cursor-pointer shadow-sm hover:shadow-md transition-shadow',
                  !props.isAdminMode ? 'border border-opacity-50 min-h-[4rem]' : 'border border-opacity-25 min-h-[2.5rem]'
                ]"
                :style="{ 
                  backgroundColor: eventGroup[0].color, 
                  color: eventGroup[0].textColor,
                  borderColor: eventGroup[0].textColor
                }"
                @click="$emit('event-click', eventGroup[0], eventGroup)"
              >
                <!-- 团队视图：紧凑显示课程名 + 气泡人数 -->
                <div v-if="props.isAdminMode" class="flex items-center justify-between">
                  <div class="flex items-center gap-1 flex-1 min-w-0">
                    <span class="font-bold truncate">{{ eventGroup[0].title }}</span>
                    <span 
                      v-if="eventGroup.length > 1"
                      class="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-white/20 text-current flex-shrink-0"
                    >
                      {{ eventGroup.length }}
                    </span>
                  </div>
                </div>
                
                <!-- 个人视图：详细分行显示，弹性布局 -->
                <div v-else class="flex flex-col h-full">
                  <!-- 课程名称 - 多行显示，强制断词确保至少2字符/行 -->
                  <div class="font-bold leading-tight break-all line-clamp-5 text-[11px] sm:text-sm">{{ eventGroup[0].title }}</div>
                  
                  <!-- 详细信息组 - 底部对齐，超窄屏自动隐藏 -->
                  <div class="mt-auto pt-1 space-y-0.5 min-[361px]:block hidden">
                    <!-- 教师 -->
                    <div v-if="eventGroup[0].instructor" class="text-[10px] sm:text-xs truncate flex items-center opacity-85">
                      <span class="w-5 sm:w-7 opacity-75 flex-shrink-0">👨‍🏫</span>
                      <span class="truncate">{{ eventGroup[0].instructor }}</span>
                    </div>
                    
                    <!-- 教室 -->
                    <div v-if="eventGroup[0].location" class="text-[10px] sm:text-xs truncate flex items-center opacity-85">
                      <span class="w-5 sm:w-7 opacity-75 flex-shrink-0">📍</span>
                      <span class="truncate">{{ eventGroup[0].location }}</span>
                    </div>
                    
                    <!-- 周数 -->
                    <div v-if="eventGroup[0].weeks_display" class="text-[10px] sm:text-xs truncate flex items-center opacity-85">
                      <span class="w-5 sm:w-7 opacity-75 flex-shrink-0">📅</span>
                      <span class="truncate">{{ eventGroup[0].weeks_display }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <!-- Single event -->
            <div
              v-else-if="eventGroup.length === 1"
              :class="[
                'rounded-md px-2 py-1 text-[11px] sm:text-xs cursor-pointer shadow-sm hover:shadow-md transition-shadow h-full',
                !props.isAdminMode ? 'border-2 border-opacity-30 min-h-[4rem]' : 'border border-opacity-25 min-h-[2.5rem]'
              ]"
              :style="{ 
                backgroundColor: eventGroup[0].color, 
                color: eventGroup[0].textColor,
                borderColor: eventGroup[0].textColor
              }"
              @click="$emit('event-click', eventGroup[0], eventGroup.length > 1 ? eventGroup : [])"
            >
              <!-- 团队视图：紧凑单行显示 -->
              <div v-if="props.isAdminMode" class="flex items-center justify-between">
                <div class="flex items-center gap-1 flex-1 min-w-0">
                  <span class="font-bold truncate">{{ eventGroup[0].title }}</span>
                </div>
              </div>
              
              <!-- 个人视图：详细分行显示，弹性布局 -->
              <div v-else class="flex flex-col h-full">
                <!-- 课程名称 - 多行显示，强制断词确保至少2字符/行 -->
                <div class="font-bold leading-tight break-all line-clamp-5 text-[11px] sm:text-sm">{{ eventGroup[0].title }}</div>
                
                <!-- 详细信息组 - 底部对齐，超窄屏自动隐藏 -->
                <div class="mt-auto pt-1 space-y-0.5 min-[361px]:block hidden">
                  <!-- 教师 -->
                  <div v-if="eventGroup[0].instructor" class="text-[10px] sm:text-xs truncate flex items-center opacity-85">
                    <span class="w-5 sm:w-7 opacity-75 flex-shrink-0">👨‍🏫</span>
                    <span class="truncate">{{ eventGroup[0].instructor }}</span>
                  </div>
                  
                  <!-- 教室 -->
                  <div v-if="eventGroup[0].location" class="text-[10px] sm:text-xs truncate flex items-center opacity-85">
                    <span class="w-5 sm:w-7 opacity-75 flex-shrink-0">📍</span>
                    <span class="truncate">{{ eventGroup[0].location }}</span>
                  </div>
                  
                  <!-- 周数 -->
                  <div v-if="eventGroup[0].weeks_display" class="text-[10px] sm:text-xs truncate flex items-center opacity-85">
                    <span class="w-5 sm:w-7 opacity-75 flex-shrink-0">📅</span>
                    <span class="truncate">{{ eventGroup[0].weeks_display }}</span>
                  </div>
                </div>
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
          class="p-4 text-center text-xs sm:text-sm font-medium text-gray-900"
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
          @click="handleDateClick(day)"
        >
          <div
            :class="[
              'text-xs sm:text-sm font-medium mb-1',
              isToday(day) ? 'bg-primary-600 text-white rounded-full w-6 h-6 flex items-center justify-center' : ''
            ]"
          >
            {{ day.getDate() }}
          </div>

          <!-- Events -->
          <div class="space-y-1">
            <div
              v-for="(eventGroup, index) in getGroupedMonthEvents(day).slice(0, 3)"
              :key="`month-group-${index}`"
              :class="[
                'text-[11px] sm:text-xs px-2 py-1 rounded cursor-pointer hover:shadow-sm transition-all border',
                !props.isAdminMode ? 'border-opacity-40 shadow-sm' : 'border-opacity-20'
              ]"
              :style="{ 
                backgroundColor: eventGroup[0].color, 
                color: eventGroup[0].textColor,
                borderColor: eventGroup[0].textColor
              }"
              @click.stop="$emit('event-click', eventGroup[0], eventGroup.length > 1 ? eventGroup : [])"
            >
              <!-- 团队视图：月视图紧凑显示 -->
              <div v-if="props.isAdminMode">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-1 flex-1 min-w-0">
                    <span class="font-bold truncate text-xs">{{ eventGroup[0].title }}</span>
                    <span 
                      v-if="eventGroup.length > 1"
                      class="inline-flex items-center px-1 py-0.5 rounded-full text-xs font-medium bg-white/25 text-current flex-shrink-0"
                    >
                      {{ eventGroup.length }}
                    </span>
                  </div>
                </div>
              </div>
              
              <!-- 个人视图：月视图详细显示 -->
              <div v-else class="space-y-0.5">
                <div class="font-bold truncate text-[11px] sm:text-xs">{{ eventGroup[0].title }}</div>
                <div v-if="eventGroup[0].instructor" class="truncate text-[11px] sm:text-xs opacity-85 flex items-center">
                  <span class="mr-1 opacity-75">👨‍🏫</span>{{ eventGroup[0].instructor }}
                </div>
                <div v-if="eventGroup[0].location" class="truncate text-[11px] sm:text-xs opacity-85 flex items-center">
                  <span class="mr-1 opacity-75">📍</span>{{ eventGroup[0].location }}
                </div>
                <div v-if="eventGroup[0].weeks_display" class="truncate text-[11px] sm:text-xs opacity-85 flex items-center">
                  <span class="mr-1 opacity-75">📅</span>{{ eventGroup[0].weeks_display }}
                </div>
              </div>
            </div>
            <div
              v-if="getGroupedMonthEvents(day).length > 3"
              class="text-[11px] sm:text-xs text-gray-500 px-2"
            >
              +{{ getGroupedMonthEvents(day).length - 3 }} 更多
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

// 添加isSameMonth函数
function isSameMonth(date1: Date, date2: Date): boolean {
  return date1.getFullYear() === date2.getFullYear() && 
         date1.getMonth() === date2.getMonth();
}

interface Props {
  events: CalendarEvent[];
  viewMode: 'week' | 'month';
  currentDate: Date;
  isAdminMode?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  isAdminMode: false,
});

const emit = defineEmits<{
  'event-click': [event: CalendarEvent, relatedEvents?: CalendarEvent[]];
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

function getDayEvents(day: Date): CalendarEvent[] {
  return props.events.filter(event => {
    const eventDate = new Date(event.start_time);
    return isSameDay(eventDate, day);
  }).sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());
}

// 新增：将同一天的事件按时间段和课程内容分组
function getGroupedDayEvents(day: Date): CalendarEvent[][] {
  const dayEvents = getDayEvents(day);
  const groups: Map<string, CalendarEvent[]> = new Map();

  dayEvents.forEach(event => {
    const startTime = new Date(event.start_time);
    const endTime = new Date(event.end_time);
    
    // 创建课程标识符：时间 + 课程名 + 教师 + 地点
    const courseKey = `${startTime.getHours()}:${startTime.getMinutes()}-${endTime.getHours()}:${endTime.getMinutes()}_${event.title}_${event.instructor || ''}_${event.location || ''}`;
    
    if (!groups.has(courseKey)) {
      groups.set(courseKey, []);
    }
    groups.get(courseKey)!.push(event);
  });

  // 按时间顺序返回分组
  return Array.from(groups.values()).sort((a, b) => {
    const aStart = new Date(a[0].start_time).getTime();
    const bStart = new Date(b[0].start_time).getTime();
    return aStart - bStart;
  });
}

// 新增：为月视图提供分组事件
function getGroupedMonthEvents(day: Date): CalendarEvent[][] {
  return getGroupedDayEvents(day);
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

// 处理时间槽点击
function handleTimeSlotClick(day: Date, timeSlotIndex: number) {
  if (props.isAdminMode) return; // 管理模式下不允许添加事件
  
  const timeSlot = timeSlots[timeSlotIndex];
  if (!timeSlot) return;
  
  // 创建日期时间对象
  const clickDate = new Date(day);
  const [hours, minutes] = timeSlot.start.split(':').map(Number);
  clickDate.setHours(hours, minutes, 0, 0);
  
  emit('date-click', clickDate);
}

// 处理日期点击（月视图）
function handleDateClick(date: Date) {
  if (props.isAdminMode) return; // 管理模式下不允许添加事件
  
  // 设置为当天的早上8:20开始
  const clickDate = new Date(date);
  clickDate.setHours(8, 20, 0, 0);
  
  emit('date-click', clickDate);
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
