<template>
  <div class="lg:flex lg:h-full lg:flex-col">
    <div class="flex flex-1 items-stretch overflow-hidden">
      <!-- Sidebar -->
      <aside class="hidden w-96 overflow-y-auto border-r border-gray-200 bg-white lg:block">
        <FilterSidebar
          :users="teamStore.userList"
          :teams="teamStore.allTeams"
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

              <div class="flex items-center gap-3">
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

            <!-- Selected filters info -->
            <div v-if="hasActiveFilters" class="mt-2 text-sm text-gray-600 space-y-1">
              <div v-if="scheduleStore.filterState.selectedUserIds.length > 0">
                已选择 {{ scheduleStore.filterState.selectedUserIds.length }} 个成员
              </div>
              <div v-if="scheduleStore.filterState.selectedTeamIds.length > 0">
                已选择 {{ scheduleStore.filterState.selectedTeamIds.length }} 个团队
              </div>
              <div v-if="scheduleStore.filterState.selectedClassNames.length > 0">
                已选择 {{ scheduleStore.filterState.selectedClassNames.length }} 个班级
              </div>
              <div v-if="scheduleStore.filterState.selectedGrades.length > 0">
                已选择 {{ scheduleStore.filterState.selectedGrades.length }} 个年级
              </div>
            </div>
          </div>

          <!-- Calendar content -->
          <div class="flex-1 overflow-hidden">
            <!-- Loading state -->
            <div v-if="scheduleStore.isLoading" class="flex justify-center items-center h-full">
              <div class="h-8 w-8 animate-spin rounded-full border-2 border-primary-600 border-t-transparent"></div>
            </div>

            <!-- Error state -->
            <div v-else-if="scheduleStore.error" class="flex justify-center items-center h-full">
              <div class="rounded-md bg-red-50 p-4">
                <div class="flex">
                  <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
                  <div class="ml-3">
                    <h3 class="text-sm font-medium text-red-800">
                      {{ scheduleStore.error }}
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
                  :teams="teamStore.allTeams"
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

    <!-- Event Modal (Admin version) -->
    <EventModal
      :is-open="isEventModalOpen"
      :event="selectedEvent"
      :is-admin="true"
      :users="teamStore.userList"
      @close="closeEventModal"
      @save="handleEventSave"
      @delete="handleEventDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useTeamStore } from '@/stores/team';
import { useScheduleStore } from '@/stores/schedule';
import FilterSidebar from '../FilterSidebar.vue';
import ScheduleCalendar from '../ScheduleCalendar.vue';
import EventModal from '../EventModal.vue';
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
  PlusIcon,
  ExclamationTriangleIcon,
  XMarkIcon,
} from '@heroicons/vue/24/outline';
import { formatDisplayDate, formatDateTime, addWeeks, addMonths } from '@/utils/date';
import { getUserColor } from '@/utils/colors';
import { apiClient } from '@/utils/api';
import type { Event, CalendarEvent, FilterState } from '@/types';

const authStore = useAuthStore();
const teamStore = useTeamStore();
const scheduleStore = useScheduleStore();

const currentDate = ref(new Date());
const viewMode = ref<'week' | 'month'>('week');
const mobileFiltersOpen = ref(false);
const isEventModalOpen = ref(false);
const selectedEvent = ref<Event | null>(null);

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
  return scheduleStore.filteredEvents.map(event => {
    const userColor = getUserColor(event.owner?.id || event.schedule_id);
    return {
      ...event,
      color: userColor.bg,
      textColor: userColor.text,
    };
  });
});

const hasActiveFilters = computed(() => {
  const fs = scheduleStore.filterState;
  return fs.selectedUserIds.length > 0 || 
         fs.selectedTeamIds.length > 0 || 
         fs.selectedClassNames.length > 0 || 
         fs.selectedGrades.length > 0 ||
         fs.nameKeyword.trim() !== '' ||
         fs.eventKeyword.trim() !== '';
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

function openCreateModal() {
  selectedEvent.value = null;
  isEventModalOpen.value = true;
}

function handleEventClick(event: Event) {
  selectedEvent.value = event;
  isEventModalOpen.value = true;
}

function handleDateClick(date: Date) {
  // Create new event at clicked date
  selectedEvent.value = {
    id: 0,
    owner_id: teamStore.userList[0]?.id || 0,
    title: '',
    description: '',
    location: '',
    start_time: formatDateTime(date),
    end_time: formatDateTime(new Date(date.getTime() + 60 * 60 * 1000)), // 1 hour later
    created_at: '',
    updated_at: '',
  };
  isEventModalOpen.value = true;
}

function closeEventModal() {
  isEventModalOpen.value = false;
  selectedEvent.value = null;
}

async function handleEventSave(eventData: any) {
  try {
    if (selectedEvent.value?.id) {
      // Update existing event (admin can update any event)
      await apiClient.updateAnyEvent(selectedEvent.value.id, eventData);
    } else {
      // Create new event for specified user
      const userId = eventData.owner_id || teamStore.userList[0]?.id;
      await apiClient.createEventForUser(userId, eventData);
    }
    
    // Refresh the events
    await scheduleStore.fetchFilteredEvents();
    closeEventModal();
  } catch (err: any) {
    console.error('Failed to save event:', err);
    // Error handling can be improved here
  }
}

async function handleEventDelete(eventId: number) {
  try {
    await apiClient.deleteAnyEvent(eventId);
    await scheduleStore.fetchFilteredEvents();
    closeEventModal();
  } catch (err: any) {
    console.error('Failed to delete event:', err);
    // Error handling can be improved here
  }
}

// Initialize
onMounted(async () => {
  // Check authentication and admin role
  await authStore.initialize();
  
  if (!authStore.isAuthenticated) {
    window.location.href = '/login';
    return;
  }

  if (!authStore.isAdmin) {
    window.location.href = '/dashboard/my-schedule';
    return;
  }

  // Load users and teams for filtering
  await teamStore.fetchUsers();
  await teamStore.fetchAllTeams();
  
  // Set initial date range and fetch events
  scheduleStore.updateDateRangeFromView();
  await scheduleStore.fetchFilteredEvents();
});
</script>
