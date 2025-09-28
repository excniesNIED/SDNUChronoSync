<template>
  <div class="lg:flex lg:h-full lg:flex-col">
    <div class="flex flex-1 items-stretch overflow-hidden">
      <!-- Sidebar -->
      <aside class="hidden w-96 overflow-y-auto border-r border-gray-200 bg-white lg:block">
        <FilterSidebar
          :users="teamStore.userList"
          :filter-state="scheduleStore.filterState"
          :all-classes="teamStore.allClasses"
          :all-grades="teamStore.allGrades"
          @update-filter="handleFilterUpdate"
          @apply-filter="handleApplyFilter"
        />
      </aside>

      <!-- Main content -->
      <main class="flex-1 overflow-hidden">
        <div class="flex h-full flex-col">
          <!-- Action bar -->
          <div class="flex-shrink-0 border-b border-gray-200 bg-white px-6 py-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-4">
                <!-- Mobile filter button -->
                <button
                  @click="mobileFiltersOpen = true"
                  class="lg:hidden inline-flex items-center gap-x-2 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                >
                  <FunnelIcon class="h-4 w-4" />
                  筛选
                </button>

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

              <!-- Selected users count -->
              <div v-if="scheduleStore.filterState.selectedUserIds.length > 0" class="text-sm text-gray-600">
                已选择 {{ scheduleStore.filterState.selectedUserIds.length }} 个成员
              </div>
            </div>
          </div>

          <!-- Calendar content -->
          <div class="flex-1 overflow-hidden">
            <!-- Loading state -->
            <div v-if="scheduleStore.filteredEventsLoading" class="flex justify-center items-center h-full">
              <div class="h-8 w-8 animate-spin rounded-full border-2 border-primary-600 border-t-transparent"></div>
            </div>

            <!-- Error state -->
            <div v-else-if="scheduleStore.filteredEventsError" class="flex justify-center items-center h-full">
              <div class="rounded-md bg-red-50 p-4">
                <div class="flex">
                  <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
                  <div class="ml-3">
                    <h3 class="text-sm font-medium text-red-800">
                      {{ scheduleStore.filteredEventsError }}
                    </h3>
                  </div>
                </div>
              </div>
            </div>

            <!-- Calendar -->
            <div v-else class="h-full bg-white">
              <ScheduleCalendar
                :events="calendarEvents"
                :view-mode="viewMode"
                :current-date="currentDate"
                :is-admin-mode="true"
                @event-click="handleEventClick"
                @date-click="handleDateClick"
              />
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Mobile filter modal -->
    <TransitionRoot as="template" :show="mobileFiltersOpen">
      <Dialog as="div" class="relative z-50 lg:hidden" @close="mobileFiltersOpen = false">
        <TransitionChild
          as="template"
          enter="transition-opacity ease-linear duration-300"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="transition-opacity ease-linear duration-300"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-gray-900/80" />
        </TransitionChild>

        <div class="fixed inset-0 flex">
          <TransitionChild
            as="template"
            enter="transition ease-in-out duration-300 transform"
            enter-from="-translate-x-full"
            enter-to="translate-x-0"
            leave="transition ease-in-out duration-300 transform"
            leave-from="translate-x-0"
            leave-to="-translate-x-full"
          >
            <DialogPanel class="relative mr-16 flex w-full max-w-xs flex-1">
              <TransitionChild
                as="template"
                enter="ease-in-out duration-300"
                enter-from="opacity-0"
                enter-to="opacity-100"
                leave="ease-in-out duration-300"
                leave-from="opacity-100"
                leave-to="opacity-0"
              >
                <div class="absolute left-full top-0 flex w-16 justify-center pt-5">
                  <button type="button" class="-m-2.5 p-2.5" @click="mobileFiltersOpen = false">
                    <span class="sr-only">关闭筛选</span>
                    <XMarkIcon class="h-6 w-6 text-white" aria-hidden="true" />
                  </button>
                </div>
              </TransitionChild>

              <div class="flex grow flex-col overflow-y-auto bg-white px-6 pb-4">
                <div class="flex h-16 shrink-0 items-center">
                  <h2 class="text-lg font-semibold text-gray-900">筛选条件</h2>
                </div>
                <FilterSidebar
                  :users="teamStore.userList"
                  :filter-state="scheduleStore.filterState"
                  :all-classes="teamStore.allClasses"
                  :all-grades="teamStore.allGrades"
                  @update-filter="handleFilterUpdate"
                  @apply-filter="handleApplyFilter"
                />
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </Dialog>
    </TransitionRoot>

    <!-- Event detail modal -->
    <TeamEventDetailModal
      :is-open="isEventDetailOpen"
      :event="selectedEvent"
      :related-events="relatedEvents"
      @close="closeEventDetail"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useTeamStore } from '@/stores/team';
import { useScheduleStore } from '@/stores/schedule';
import FilterSidebar from './FilterSidebar.vue';
import ScheduleCalendar from './ScheduleCalendar.vue';
import EventDetailModal from './EventDetailModal.vue';
import TeamEventDetailModal from './TeamEventDetailModal.vue';
import {
  Dialog,
  DialogPanel,
  TransitionChild,
  TransitionRoot,
} from '@headlessui/vue';
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  FunnelIcon,
  ExclamationTriangleIcon,
  XMarkIcon,
} from '@heroicons/vue/24/outline';
import { formatDisplayDate, addWeeks, addMonths } from '@/utils/date';
import { getUserColor } from '@/utils/colors';
import type { Event, CalendarEvent, FilterState } from '@/types';

const authStore = useAuthStore();
const teamStore = useTeamStore();
const scheduleStore = useScheduleStore();

const currentDate = ref(new Date());
const viewMode = ref<'week' | 'month'>('week');
const mobileFiltersOpen = ref(false);
const isEventDetailOpen = ref(false);
const selectedEvent = ref<Event | null>(null);
const relatedEvents = ref<Event[]>([]);

// Computed properties
const currentDateTitle = computed(() => {
  if (viewMode.value === 'week') {
    return `${formatDisplayDate(currentDate.value)} 周`;
  } else {
    return `${currentDate.value.getFullYear()}年${currentDate.value.getMonth() + 1}月`;
  }
});

const calendarEvents = computed((): CalendarEvent[] => {
  if (!scheduleStore.filteredEvents || scheduleStore.filteredEvents.length === 0) {
    return [];
  }
  
  return scheduleStore.filteredEvents.map(event => {
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
  
  // Update date range and fetch new data
  scheduleStore.updateDateRangeFromView();
  handleApplyFilter();
}

function handleFilterUpdate(newFilter: Partial<FilterState>) {
  scheduleStore.updateFilter(newFilter);
}

async function handleApplyFilter() {
  await scheduleStore.fetchFilteredEvents();
}

function handleEventClick(event: Event, relatedEventsFromCalendar?: Event[]) {
  selectedEvent.value = event;
  
  // 如果日历组件已经提供了相关事件，直接使用；否则查找
  if (relatedEventsFromCalendar && relatedEventsFromCalendar.length > 0) {
    relatedEvents.value = relatedEventsFromCalendar.filter(e => e.id !== event.id);
  } else {
    // 查找同一时间段、同一课程的所有相关事件
    relatedEvents.value = findRelatedEvents(event);
  }
  
  isEventDetailOpen.value = true;
}

// 查找相关事件（同一课程名称、同一时间段）
function findRelatedEvents(targetEvent: Event): Event[] {
  if (!scheduleStore.filteredEvents) {
    return [];
  }

  return scheduleStore.filteredEvents.filter(event => {
    // 排除当前事件本身
    if (event.id === targetEvent.id) {
      return false;
    }
    
    // 同一课程名称
    if (event.title !== targetEvent.title) {
      return false;
    }
    
    // 同一时间段
    const eventStart = new Date(event.start_time);
    const eventEnd = new Date(event.end_time);
    const targetStart = new Date(targetEvent.start_time);
    const targetEnd = new Date(targetEvent.end_time);
    
    // 检查时间是否重叠
    const timeMatches = (
      eventStart.getTime() === targetStart.getTime() &&
      eventEnd.getTime() === targetEnd.getTime()
    );
    
    if (!timeMatches) {
      return false;
    }
    
    // 可选：同一教师
    if (targetEvent.instructor && event.instructor !== targetEvent.instructor) {
      return false;
    }
    
    return true;
  });
}

function handleDateClick(date: Date) {
  // For team view, we don't create events on date click
  // This could be extended for admin functionality
}

function closeEventDetail() {
  isEventDetailOpen.value = false;
  selectedEvent.value = null;
  relatedEvents.value = [];
}

// Initialize
onMounted(async () => {
  // Check authentication
  await authStore.initialize();
  
  if (!authStore.isAuthenticated) {
    window.location.href = '/login';
    return;
  }

  // Load users for filtering
  await teamStore.fetchUsers();
  
  // Set initial date range and fetch events
  scheduleStore.updateDateRangeFromView();
  await scheduleStore.fetchFilteredEvents();
});
</script>
