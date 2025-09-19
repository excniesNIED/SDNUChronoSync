import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Event, ScheduleFilter, CalendarViewMode, FilterState } from '@/types';
import { apiClient } from '@/utils/api';
import { formatDate, getWeekStart, getWeekEnd, getMonthStart, getMonthEnd } from '@/utils/date';

export const useScheduleStore = defineStore('schedule', () => {
  // State
  const events = ref<Event[]>([]);
  const myEvents = ref<Event[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // View state
  const viewMode = ref<CalendarViewMode>({
    type: 'week',
    date: new Date(),
  });

  // Filter state
  const filterState = ref<FilterState>({
    dateRange: {
      start: formatDate(getWeekStart(new Date())),
      end: formatDate(getWeekEnd(new Date())),
    },
    selectedUserIds: [],
    className: '',
    grade: '',
    nameKeyword: '',
    eventKeyword: '',
  });

  // Getters
  const currentEvents = computed(() => events.value);
  const currentMyEvents = computed(() => myEvents.value);

  const filteredEvents = computed(() => {
    return events.value.filter(event => {
      const eventDate = new Date(event.start_time);
      const startDate = new Date(filterState.value.dateRange.start);
      const endDate = new Date(filterState.value.dateRange.end);

      // Date range filter
      if (eventDate < startDate || eventDate > endDate) {
        return false;
      }

      // User filter
      if (filterState.value.selectedUserIds.length > 0 && 
          !filterState.value.selectedUserIds.includes(event.owner_id)) {
        return false;
      }

      // Class filter
      if (filterState.value.className && 
          event.owner?.class_name !== filterState.value.className) {
        return false;
      }

      // Grade filter
      if (filterState.value.grade && 
          event.owner?.grade !== filterState.value.grade) {
        return false;
      }

      // Name keyword filter
      if (filterState.value.nameKeyword && 
          !event.owner?.full_name.includes(filterState.value.nameKeyword)) {
        return false;
      }

      // Event keyword filter
      if (filterState.value.eventKeyword && 
          !event.title.includes(filterState.value.eventKeyword)) {
        return false;
      }

      return true;
    });
  });

  const currentViewDateRange = computed(() => {
    if (viewMode.value.type === 'week') {
      return {
        start: getWeekStart(viewMode.value.date),
        end: getWeekEnd(viewMode.value.date),
      };
    } else {
      return {
        start: getMonthStart(viewMode.value.date),
        end: getMonthEnd(viewMode.value.date),
      };
    }
  });

  // Actions
  async function fetchMyEvents(): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      const fetchedEvents = await apiClient.getMyEvents();
      myEvents.value = fetchedEvents;
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取个人日程失败';
      console.error('Failed to fetch my events:', err);
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchFilteredEvents(): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      const filter: ScheduleFilter = {
        start_date: filterState.value.dateRange.start,
        end_date: filterState.value.dateRange.end,
        user_ids: filterState.value.selectedUserIds.length > 0 
          ? filterState.value.selectedUserIds.join(',') 
          : undefined,
        class_name: filterState.value.className || undefined,
        grade: filterState.value.grade || undefined,
        full_name_contains: filterState.value.nameKeyword || undefined,
        event_title_contains: filterState.value.eventKeyword || undefined,
      };

      const fetchedEvents = await apiClient.getFilteredSchedule(filter);
      events.value = fetchedEvents;
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取团队日程失败';
      console.error('Failed to fetch filtered events:', err);
    } finally {
      isLoading.value = false;
    }
  }

  async function createEvent(eventData: any): Promise<Event | null> {
    isLoading.value = true;
    error.value = null;

    try {
      const newEvent = await apiClient.createMyEvent(eventData);
      myEvents.value.push(newEvent);
      return newEvent;
    } catch (err: any) {
      error.value = err.response?.data?.detail || '创建日程失败';
      console.error('Failed to create event:', err);
      return null;
    } finally {
      isLoading.value = false;
    }
  }

  async function updateEvent(eventId: number, eventData: any): Promise<Event | null> {
    isLoading.value = true;
    error.value = null;

    try {
      const updatedEvent = await apiClient.updateMyEvent(eventId, eventData);
      
      // Update in myEvents array
      const index = myEvents.value.findIndex(e => e.id === eventId);
      if (index !== -1) {
        myEvents.value[index] = updatedEvent;
      }

      // Update in events array if it exists there
      const teamIndex = events.value.findIndex(e => e.id === eventId);
      if (teamIndex !== -1) {
        events.value[teamIndex] = updatedEvent;
      }

      return updatedEvent;
    } catch (err: any) {
      error.value = err.response?.data?.detail || '更新日程失败';
      console.error('Failed to update event:', err);
      return null;
    } finally {
      isLoading.value = false;
    }
  }

  async function deleteEvent(eventId: number): Promise<boolean> {
    isLoading.value = true;
    error.value = null;

    try {
      await apiClient.deleteMyEvent(eventId);
      
      // Remove from myEvents array
      myEvents.value = myEvents.value.filter(e => e.id !== eventId);
      
      // Remove from events array
      events.value = events.value.filter(e => e.id !== eventId);

      return true;
    } catch (err: any) {
      error.value = err.response?.data?.detail || '删除日程失败';
      console.error('Failed to delete event:', err);
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function exportSchedule(): Promise<void> {
    try {
      const blob = await apiClient.exportMySchedule();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'my_schedule.ics';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      error.value = err.response?.data?.detail || '导出日程失败';
      console.error('Failed to export schedule:', err);
    }
  }

  // View actions
  function setViewMode(mode: CalendarViewMode): void {
    viewMode.value = mode;
    updateDateRangeFromView();
  }

  function updateDateRangeFromView(): void {
    const range = currentViewDateRange.value;
    filterState.value.dateRange = {
      start: formatDate(range.start),
      end: formatDate(range.end),
    };
  }

  function updateFilter(newFilter: Partial<FilterState>): void {
    filterState.value = { ...filterState.value, ...newFilter };
  }

  function clearError(): void {
    error.value = null;
  }

  return {
    // State
    events,
    myEvents,
    isLoading,
    error,
    viewMode,
    filterState,

    // Getters
    currentEvents,
    currentMyEvents,
    filteredEvents,
    currentViewDateRange,

    // Actions
    fetchMyEvents,
    fetchFilteredEvents,
    createEvent,
    updateEvent,
    deleteEvent,
    exportSchedule,
    setViewMode,
    updateDateRangeFromView,
    updateFilter,
    clearError,
  };
});
