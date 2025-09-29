import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { apiClient } from '../utils/api'
import type { ScheduleResponse, ScheduleCreate, ScheduleUpdate, Event, CreateEventRequest, UpdateEventRequest, CalendarViewMode, FilterState } from '../types'

export const useScheduleStore = defineStore('schedule', () => {
  // State
  const schedules = ref<ScheduleResponse[]>([])
  const activeScheduleId = ref<number | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  // Event state
  const currentMyEvents = ref<Event[]>([])
  const eventsLoading = ref(false)
  const eventsError = ref<string | null>(null)
  
  // Team view filtered events
  const filteredEvents = ref<Event[]>([])
  const filteredEventsLoading = ref(false)
  const filteredEventsError = ref<string | null>(null)
  
  // View state
  const viewMode = ref<CalendarViewMode>({ type: 'week', date: new Date() })
  
  // Filter state for team view
  const filterState = ref<FilterState>({
    dateRange: {
      start: new Date().toISOString().split('T')[0],
      end: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    },
    selectedUserIds: [],
    selectedTeamIds: [],
    selectedClassNames: [],
    selectedGrades: [],
    nameKeyword: '',
    eventKeyword: ''
  })

  // Getters
  const activeSchedule = computed(() => {
    if (!activeScheduleId.value) return null
    return schedules.value.find(s => s.id === activeScheduleId.value) || null
  })

  const activeSchedules = computed(() => {
    return schedules.value.filter(s => s.status === '进行')
  })

  // Actions
  async function fetchSchedules() {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.getSchedules()
      schedules.value = response
      
      // 从localStorage恢复activeScheduleId
      const savedActiveId = localStorage.getItem('activeScheduleId')
      if (savedActiveId && schedules.value.some(s => s.id === parseInt(savedActiveId))) {
        activeScheduleId.value = parseInt(savedActiveId)
      } else if (!activeScheduleId.value && activeSchedules.value.length > 0) {
        // 如果没有设置活跃课表，自动选择第一个进行中的课表
        setActiveSchedule(activeSchedules.value[0].id)
      }
      
      // 自动加载活跃课表的事件
      if (activeScheduleId.value) {
        await fetchMyEvents()
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取课表列表失败'
      console.error('Failed to fetch schedules:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function createSchedule(scheduleData: ScheduleCreate) {
    isLoading.value = true
    error.value = null

    try {
      const newSchedule = await apiClient.createSchedule(scheduleData)
      schedules.value.push(newSchedule)
      
      // 自动设置为活跃课表
      activeScheduleId.value = newSchedule.id
      
      return newSchedule
    } catch (err: any) {
      error.value = err.response?.data?.detail || '创建课表失败'
      console.error('Failed to create schedule:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateSchedule(scheduleId: number, updateData: ScheduleUpdate) {
    isLoading.value = true
    error.value = null

    try {
      const updatedSchedule = await apiClient.updateSchedule(scheduleId, updateData)
      
      const index = schedules.value.findIndex(s => s.id === scheduleId)
      if (index !== -1) {
        schedules.value[index] = updatedSchedule
      }
      
      return updatedSchedule
    } catch (err: any) {
      error.value = err.response?.data?.detail || '更新课表失败'
      console.error('Failed to update schedule:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteSchedule(scheduleId: number) {
    isLoading.value = true
    error.value = null

    try {
      await apiClient.deleteSchedule(scheduleId)
      
      schedules.value = schedules.value.filter(s => s.id !== scheduleId)
      
      // 如果删除的是当前活跃课表，重新选择
      if (activeScheduleId.value === scheduleId) {
        activeScheduleId.value = activeSchedules.value.length > 0 ? activeSchedules.value[0].id : null
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || '删除课表失败'
      console.error('Failed to delete schedule:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function setActiveSchedule(scheduleId: number | null) {
    if (scheduleId === null || schedules.value.some(s => s.id === scheduleId)) {
      activeScheduleId.value = scheduleId
      
      // 保存到localStorage
      if (scheduleId) {
        localStorage.setItem('activeScheduleId', scheduleId.toString())
        // 自动加载新的活跃课表的事件
        fetchMyEvents()
      } else {
        localStorage.removeItem('activeScheduleId')
        currentMyEvents.value = []
      }
    }
  }

  function clearError() {
    error.value = null
    eventsError.value = null
    filteredEventsError.value = null
  }

  function resetStore() {
    schedules.value = []
    activeScheduleId.value = null
    isLoading.value = false
    error.value = null
    currentMyEvents.value = []
    eventsLoading.value = false
    eventsError.value = null
    filteredEvents.value = []
    filteredEventsLoading.value = false
    filteredEventsError.value = null
    localStorage.removeItem('activeScheduleId')
  }
  
  // Event management functions
  async function fetchMyEvents() {
    eventsLoading.value = true
    eventsError.value = null

    try {
      // 使用个人课表API而不是多课表API
      const events = await apiClient.getMyEvents()
      currentMyEvents.value = events
    } catch (err: any) {
      eventsError.value = err.response?.data?.detail || '获取事件失败'
      console.error('Failed to fetch events:', err)
    } finally {
      eventsLoading.value = false
    }
  }

  async function createEvent(eventData: CreateEventRequest) {
    try {
      // 使用个人课表API创建事件
      const newEvent = await apiClient.createMyEvent(eventData)
      currentMyEvents.value.push(newEvent)
      return newEvent
    } catch (err: any) {
      eventsError.value = err.response?.data?.detail || '创建事件失败'
      console.error('Failed to create event:', err)
      throw err
    }
  }

  async function updateEvent(eventId: number, eventData: UpdateEventRequest) {
    try {
      // 使用个人课表API更新事件
      const updatedEvent = await apiClient.updateMyEvent(eventId, eventData)
      
      const index = currentMyEvents.value.findIndex(e => e.id === eventId)
      if (index !== -1) {
        currentMyEvents.value[index] = updatedEvent
      }
      
      return updatedEvent
    } catch (err: any) {
      eventsError.value = err.response?.data?.detail || '更新事件失败'
      console.error('Failed to update event:', err)
      throw err
    }
  }

  async function deleteEvent(eventId: number) {
    try {
      // 使用个人课表API删除事件
      await apiClient.deleteMyEvent(eventId)
      currentMyEvents.value = currentMyEvents.value.filter(e => e.id !== eventId)
    } catch (err: any) {
      eventsError.value = err.response?.data?.detail || '删除事件失败'
      console.error('Failed to delete event:', err)
      throw err
    }
  }

  async function exportSchedule() {
    try {
      // 使用个人课表导出API
      const blob = await apiClient.exportMySchedule()
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `my-schedule-${new Date().toISOString().split('T')[0]}.ics`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (err: any) {
      eventsError.value = err.response?.data?.detail || '导出失败'
      console.error('Failed to export schedule:', err)
      throw err
    }
  }

  function setViewMode(mode: CalendarViewMode) {
    viewMode.value = mode
  }
  
  // Team view methods
  async function fetchFilteredEvents() {
    filteredEventsLoading.value = true
    filteredEventsError.value = null

    try {
      const filter = {
        start_date: filterState.value.dateRange.start,
        end_date: filterState.value.dateRange.end,
        user_ids: filterState.value.selectedUserIds.length > 0 ? filterState.value.selectedUserIds.join(',') : undefined,
        team_ids: filterState.value.selectedTeamIds.length > 0 ? filterState.value.selectedTeamIds.join(',') : undefined,
        class_name: filterState.value.selectedClassNames.length > 0 ? filterState.value.selectedClassNames.join(',') : undefined,
        grade: filterState.value.selectedGrades.length > 0 ? filterState.value.selectedGrades.join(',') : undefined,
        full_name_contains: filterState.value.nameKeyword || undefined,
        event_title_contains: filterState.value.eventKeyword || undefined
      }
      
      const events = await apiClient.getFilteredSchedule(filter)
      filteredEvents.value = events
    } catch (err: any) {
      filteredEventsError.value = err.response?.data?.detail || '获取团队日程失败'
      console.error('Failed to fetch filtered events:', err)
    } finally {
      filteredEventsLoading.value = false
    }
  }

  function updateFilter(newFilter: Partial<FilterState>) {
    filterState.value = { ...filterState.value, ...newFilter }
  }

  function updateDateRangeFromView() {
    const currentDate = viewMode.value.date
    let startDate: Date
    let endDate: Date

    if (viewMode.value.type === 'week') {
      // Get start of week (Monday)
      const day = currentDate.getDay()
      const diff = currentDate.getDate() - day + (day === 0 ? -6 : 1)
      startDate = new Date(currentDate)
      startDate.setDate(diff)
      
      // Get end of week (Sunday)
      endDate = new Date(startDate)
      endDate.setDate(startDate.getDate() + 6)
    } else {
      // Get start of month
      startDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1)
      // Get end of month
      endDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0)
    }

    filterState.value.dateRange.start = startDate.toISOString().split('T')[0]
    filterState.value.dateRange.end = endDate.toISOString().split('T')[0]
  }

  return {
    // State
    schedules,
    activeScheduleId,
    isLoading,
    error,
    currentMyEvents,
    eventsLoading,
    eventsError,
    filteredEvents,
    filteredEventsLoading,
    filteredEventsError,
    viewMode,
    filterState,
    
    // Getters
    activeSchedule,
    activeSchedules,
    
    // Schedule Actions
    fetchSchedules,
    createSchedule,
    updateSchedule,
    deleteSchedule,
    setActiveSchedule,
    
    // Event Actions
    fetchMyEvents,
    createEvent,
    updateEvent,
    deleteEvent,
    exportSchedule,
    setViewMode,
    
    // Team View Actions
    fetchFilteredEvents,
    updateFilter,
    updateDateRangeFromView,
    
    // Utility
    clearError,
    resetStore
  }
})