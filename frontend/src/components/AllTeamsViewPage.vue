<template>
  <div class="lg:flex lg:h-full lg:flex-col">
    <div class="flex flex-1 items-stretch overflow-hidden">
      <!-- Sidebar -->
      <aside class="hidden w-96 overflow-y-auto border-r border-gray-200 bg-white lg:block">
        <FilterSidebar
          :users="allTeamMembers"
          :teams="myTeams"
          :filter-state="scheduleStore.filterState"
          :all-classes="allClasses"
          :all-grades="allGrades"
          @update-filter="handleFilterUpdate"
          @apply-filter="handleApplyFilter"
        />
      </aside>

      <!-- Main content -->
      <main class="flex-1 overflow-hidden">
        <div class="flex h-full flex-col">
          <!-- Action bar -->
          <div class="flex-shrink-0 border-b border-gray-200 bg-white px-4 md:px-6 py-3 md:py-4">
            <!-- 主要操作区域 - 使用 flex-wrap 支持换行 -->
            <div class="flex flex-wrap items-center gap-3 mb-3">
              <!-- 左侧控制组 -->
              <div class="flex items-center gap-2 flex-wrap">
                <!-- Mobile filter button -->
                <button
                  @click="mobileFiltersOpen = true"
                  class="lg:hidden inline-flex items-center gap-x-1.5 rounded-md bg-white px-2.5 py-1.5 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                >
                  <FunnelIcon class="h-4 w-4" />
                  <span class="hidden sm:inline">筛选</span>
                </button>

                <!-- View mode toggle (button style for larger screens, dropdown for smaller) -->
                <div class="hidden lg:flex rounded-md shadow-sm">
                  <button
                    @click="setViewMode('week')"
                    :class="[
                      viewMode === 'week'
                        ? 'bg-primary-600 text-white'
                        : 'bg-white text-gray-700 hover:bg-gray-50',
                      'relative inline-flex items-center rounded-l-md px-3 py-1.5 text-sm font-semibold ring-1 ring-inset ring-gray-300 focus:z-10'
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
                      'relative -ml-px inline-flex items-center rounded-r-md px-3 py-1.5 text-sm font-semibold ring-1 ring-inset ring-gray-300 focus:z-10'
                    ]"
                  >
                    <span class="hidden xl:inline">月视图</span>
                    <span class="xl:hidden">月</span>
                  </button>
                </div>

                <!-- View mode dropdown for smaller screens -->
                <div class="lg:hidden">
                  <Menu as="div" class="relative inline-block text-left">
                    <div>
                      <MenuButton class="inline-flex w-full justify-center gap-x-1 rounded-md bg-white px-2.5 py-1.5 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                        {{ viewMode === 'week' ? '周' : '月' }}
                        <ChevronDownIcon class="-mr-0.5 h-4 w-4 text-gray-400" />
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
              </div>

              <!-- Date navigation - 可在中等屏幕换行 -->
              <div class="flex items-center gap-1.5 md:gap-2">
                <button
                  @click="navigateDate(-1)"
                  class="p-1.5 md:p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100 transition-colors"
                  title="上一周/月"
                >
                  <ChevronLeftIcon class="h-5 w-5" />
                </button>
                <h2 class="text-base md:text-lg font-semibold text-gray-900 min-w-[140px] md:min-w-[180px] text-center">
                  {{ currentDateTitle }}
                </h2>
                <button
                  @click="navigateDate(1)"
                  class="p-1.5 md:p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100 transition-colors"
                  title="下一周/月"
                >
                  <ChevronRightIcon class="h-5 w-5" />
                </button>
              </div>

              <!-- Quick action buttons -->
              <div class="flex items-center gap-2">
                <button
                  @click="jumpToToday"
                  class="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium bg-green-100 text-green-700 hover:bg-green-200 rounded-md transition-colors"
                  title="跳转到今天"
                >
                  <CalendarIcon class="h-3.5 w-3.5" />
                  <span>今天</span>
                </button>
                
                <button
                  @click="forceRefreshEvents"
                  class="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium bg-blue-100 text-blue-700 hover:bg-blue-200 rounded-md transition-colors"
                  title="强制刷新数据"
                >
                  <ArrowPathIcon class="h-3.5 w-3.5" />
                  <span>刷新</span>
                </button>
              </div>
            </div>

            <!-- Team info and filter status - 独立的信息栏 -->
            <div class="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm">
              <div class="inline-flex items-center gap-2">
                <span class="font-medium text-gray-700">
                  {{ selectedTeamsCount > 0 ? `已选择 ${selectedTeamsCount} 个团队` : '全部团队' }}
                </span>
                <span v-if="totalMembersCount > 0" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                  {{ totalMembersCount }} 人
                </span>
              </div>
              
              <!-- 筛选状态标签 -->
              <div v-if="hasActiveFilters" class="flex flex-wrap items-center gap-2">
                <span v-if="scheduleStore.filterState.selectedUserIds.length > 0" 
                  class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-700">
                  已筛选 {{ scheduleStore.filterState.selectedUserIds.length }} 个成员
                </span>
                <span v-if="scheduleStore.filterState.selectedClassNames.length > 0" 
                  class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                  {{ scheduleStore.filterState.selectedClassNames.length }} 个班级
                </span>
                <span v-if="scheduleStore.filterState.selectedGrades.length > 0" 
                  class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700">
                  {{ scheduleStore.filterState.selectedGrades.length }} 个年级
                </span>
              </div>
            </div>
          </div>

          <!-- Calendar content -->
          <div class="flex-1 overflow-hidden">
            <!-- Loading state -->
            <div v-if="loading" class="flex justify-center items-center h-full">
              <div class="h-8 w-8 animate-spin rounded-full border-2 border-primary-600 border-t-transparent"></div>
            </div>

            <!-- Error state -->
            <div v-else-if="error" class="flex justify-center items-center h-full">
              <div class="rounded-md bg-red-50 p-4">
                <div class="flex">
                  <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
                  <div class="ml-3">
                    <h3 class="text-sm font-medium text-red-800">
                      {{ error }}
                    </h3>
                  </div>
                </div>
              </div>
            </div>

            <!-- Empty state -->
            <div v-else-if="myTeams.length === 0" class="flex justify-center items-center h-full">
              <div class="text-center">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                <h3 class="mt-2 text-sm font-medium text-gray-900">还没有加入任何团队</h3>
                <p class="mt-1 text-sm text-gray-500">先加入一个团队才能查看团队课表</p>
                <div class="mt-6">
                  <a
                    href="/dashboard/my-teams"
                    class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    前往我的团队
                  </a>
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
                  :users="allTeamMembers"
                  :teams="myTeams"
                  :filter-state="scheduleStore.filterState"
                  :all-classes="allClasses"
                  :all-grades="allGrades"
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
import { ref, computed, onMounted, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useTeamStore } from '@/stores/team';
import { useScheduleStore } from '@/stores/schedule';
import FilterSidebar from './FilterSidebar.vue';
import ScheduleCalendar from './ScheduleCalendar.vue';
import TeamEventDetailModal from './TeamEventDetailModal.vue';

// Props
interface Props {
  preselectedTeamId?: number;
}

const props = withDefaults(defineProps<Props>(), {
  preselectedTeamId: undefined
});

import {
  Dialog,
  DialogPanel,
  Menu,
  MenuButton,
  MenuItem,
  MenuItems,
  TransitionChild,
  TransitionRoot,
} from '@headlessui/vue';
import {
  ChevronDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  FunnelIcon,
  ExclamationTriangleIcon,
  XMarkIcon,
  CalendarIcon,
  ArrowPathIcon,
} from '@heroicons/vue/24/outline';
import { formatDisplayDate, addWeeks, addMonths } from '@/utils/date';
import { generateEventColor } from '@/utils/colors';
import type { Event, CalendarEvent, FilterState, Team, User } from '@/types';

const authStore = useAuthStore();
const teamStore = useTeamStore();
const scheduleStore = useScheduleStore();

const currentDate = ref(new Date());
const viewMode = ref<'week' | 'month'>('week');
const mobileFiltersOpen = ref(false);
const isEventDetailOpen = ref(false);
const selectedEvent = ref<Event | null>(null);
const relatedEvents = ref<Event[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);

// Computed properties
const myTeams = computed(() => teamStore.teams);

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
  return scheduleStore.filteredEvents.map(event => {
    const color = generateEventColor(event.owner?.full_name || 'Unknown');
    return {
      ...event,
      color: color,
      textColor: '#ffffff',
    };
  });
});

const allTeamMembers = computed((): User[] => {
  const membersMap = new Map<number, User>();
  
  myTeams.value.forEach(team => {
    team.members?.forEach(member => {
      membersMap.set(member.id, member);
    });
  });
  
  return Array.from(membersMap.values());
});

const allClasses = computed(() => {
  const classes = new Set<string>();
  allTeamMembers.value.forEach(member => {
    if (member.class_name) {
      classes.add(member.class_name);
    }
  });
  return Array.from(classes);
});

const allGrades = computed(() => {
  const grades = new Set<string>();
  allTeamMembers.value.forEach(member => {
    if (member.grade) {
      grades.add(member.grade);
    }
  });
  return Array.from(grades);
});

const hasActiveFilters = computed(() => {
  const fs = scheduleStore.filterState;
  return fs.selectedUserIds.length > 0 || 
         fs.selectedClassNames.length > 0 || 
         fs.selectedGrades.length > 0 ||
         fs.nameKeyword.trim() !== '' ||
         fs.eventKeyword.trim() !== '';
});

const selectedTeamsCount = computed(() => {
  return scheduleStore.filterState.selectedTeamIds.length;
});

const totalMembersCount = computed(() => {
  if (selectedTeamsCount.value === 0) {
    // Show all members count
    return allTeamMembers.value.length;
  }
  
  // Show members count for selected teams
  const selectedTeams = myTeams.value.filter(team => 
    scheduleStore.filterState.selectedTeamIds.includes(team.id)
  );
  
  const membersMap = new Map<number, User>();
  selectedTeams.forEach(team => {
    team.members?.forEach(member => {
      membersMap.set(member.id, member);
    });
  });
  
  return membersMap.size;
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

function jumpToToday() {
  currentDate.value = new Date();
  console.log(`跳转到今天: ${currentDate.value.toLocaleDateString('zh-CN')}`);
  
  scheduleStore.setViewMode({
    type: viewMode.value,
    date: currentDate.value,
  });
  
  // Update date range and fetch new data
  scheduleStore.updateDateRangeFromView();
  handleApplyFilter();
}

async function forceRefreshEvents() {
  try {
    console.log('强制刷新团队数据...');
    
    // Reload teams
    await teamStore.fetchMyTeams();
    
    // Refresh events
    await handleApplyFilter();
    
    console.log('团队数据刷新完成');
    
  } catch (error) {
    console.error('刷新团队数据失败:', error);
  }
}

function handleFilterUpdate(newFilter: Partial<FilterState>) {
  scheduleStore.updateFilter(newFilter);
}

async function handleApplyFilter() {
  // If no teams are selected, select all teams by default
  if (scheduleStore.filterState.selectedTeamIds.length === 0 && myTeams.value.length > 0) {
    const allTeamIds = myTeams.value.map(team => team.id);
    scheduleStore.updateFilter({ selectedTeamIds: allTeamIds });
  }
  
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

  // Load teams
  loading.value = true;
  error.value = null;
  
  try {
    await teamStore.fetchMyTeams();
    
    // Initialize schedule store
    scheduleStore.setViewMode({
      type: viewMode.value,
      date: currentDate.value,
    });
    scheduleStore.updateDateRangeFromView();
    
    // If preselected team ID is provided, set it as the initial filter
    if (props.preselectedTeamId && myTeams.value.some(t => t.id === props.preselectedTeamId)) {
      scheduleStore.updateFilter({ selectedTeamIds: [props.preselectedTeamId] });
    } else {
      // Otherwise, select all teams by default
      const allTeamIds = myTeams.value.map(team => team.id);
      scheduleStore.updateFilter({ selectedTeamIds: allTeamIds });
    }
    
    // Fetch initial events
    await handleApplyFilter();
    
  } catch (err: any) {
    console.error('Failed to load teams:', err);
    error.value = err.response?.data?.detail || '加载团队数据失败';
  } finally {
    loading.value = false;
  }
});

// Watch for preselectedTeamId changes
watch(() => props.preselectedTeamId, async (newTeamId) => {
  if (newTeamId && myTeams.value.some(t => t.id === newTeamId)) {
    scheduleStore.updateFilter({ selectedTeamIds: [newTeamId] });
    await handleApplyFilter();
  }
});
</script>
