import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { apiClient } from '@/utils/api';
import type { Team, TeamCreate, TeamUpdate, TeamJoinRequest, TeamMemberAdd, User, Event } from '@/types';

export const useTeamStore = defineStore('team', () => {
  // State
  const teams = ref<Team[]>([]);
  const currentTeam = ref<Team | null>(null);
  const teamEvents = ref<Event[]>([]);
  const allTeams = ref<Team[]>([]);  // For admin use
  const userList = ref<User[]>([]);  // For admin user management
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const getTeamById = computed(() => {
    return (id: number) => teams.value.find(team => team.id === id);
  });

  // User-related computed properties for admin use
  const allClasses = computed(() => {
    const classes = [...new Set(userList.value.map(user => user.class_name))];
    return classes.filter(Boolean).sort();
  });

  const allGrades = computed(() => {
    const grades = [...new Set(userList.value.map(user => user.grade))];
    return grades.filter(Boolean).sort();
  });

  const isTeamCreator = computed(() => {
    return (teamId: number, userId: number) => {
      const team = getTeamById.value(teamId);
      return team?.creator_id === userId;
    };
  });

  const isTeamMember = computed(() => {
    return (teamId: number, userId: number) => {
      const team = getTeamById.value(teamId);
      return team?.members?.some(member => member.id === userId) || false;
    };
  });

  // Actions
  async function fetchMyTeams() {
    try {
      loading.value = true;
      error.value = null;
      const data = await apiClient.getMyTeams();
      teams.value = data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取团队列表失败';
      console.error('Failed to fetch teams:', err);
    } finally {
      loading.value = false;
    }
  }

  async function fetchTeam(teamId: number) {
    try {
      loading.value = true;
      error.value = null;
      const team = await apiClient.getTeam(teamId);
      currentTeam.value = team;
      
      // Update the team in the list if it exists
      const index = teams.value.findIndex(t => t.id === teamId);
      if (index !== -1) {
        teams.value[index] = team;
      }
      
      return team;
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取团队信息失败';
      console.error('Failed to fetch team:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function createTeam(teamData: TeamCreate) {
    try {
      loading.value = true;
      error.value = null;
      const newTeam = await apiClient.createTeam(teamData);
      teams.value.push(newTeam);
      return newTeam;
    } catch (err: any) {
      error.value = err.response?.data?.detail || '创建团队失败';
      console.error('Failed to create team:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updateTeam(teamId: number, teamData: TeamUpdate) {
    try {
      loading.value = true;
      error.value = null;
      const updatedTeam = await apiClient.updateTeam(teamId, teamData);
      
      // Update the team in the list
      const index = teams.value.findIndex(t => t.id === teamId);
      if (index !== -1) {
        teams.value[index] = updatedTeam;
      }
      
      // Update current team if it's the same
      if (currentTeam.value?.id === teamId) {
        currentTeam.value = updatedTeam;
      }
      
      return updatedTeam;
    } catch (err: any) {
      error.value = err.response?.data?.detail || '更新团队失败';
      console.error('Failed to update team:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteTeam(teamId: number) {
    try {
      loading.value = true;
      error.value = null;
      await apiClient.deleteTeam(teamId);
      
      // Remove from teams list
      teams.value = teams.value.filter(t => t.id !== teamId);
      
      // Clear current team if it's the same
      if (currentTeam.value?.id === teamId) {
        currentTeam.value = null;
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || '删除团队失败';
      console.error('Failed to delete team:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function joinTeam(joinData: TeamJoinRequest) {
    try {
      loading.value = true;
      error.value = null;
      const team = await apiClient.joinTeam(joinData);
      
      // Add to teams list if not already there
      const exists = teams.value.find(t => t.id === team.id);
      if (!exists) {
        teams.value.push(team);
      }
      
      return team;
    } catch (err: any) {
      error.value = err.response?.data?.detail || '加入团队失败';
      console.error('Failed to join team:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function leaveTeam(teamId: number) {
    try {
      loading.value = true;
      error.value = null;
      await apiClient.leaveTeam(teamId);
      
      // Remove from teams list
      teams.value = teams.value.filter(t => t.id !== teamId);
      
      // Clear current team if it's the same
      if (currentTeam.value?.id === teamId) {
        currentTeam.value = null;
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || '退出团队失败';
      console.error('Failed to leave team:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function addTeamMember(teamId: number, memberData: TeamMemberAdd) {
    try {
      loading.value = true;
      error.value = null;
      await apiClient.addTeamMember(teamId, memberData);
      
      // Refresh team data to get updated members
      await fetchTeam(teamId);
    } catch (err: any) {
      error.value = err.response?.data?.detail || '添加成员失败';
      console.error('Failed to add team member:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function removeTeamMember(teamId: number, userId: number) {
    try {
      loading.value = true;
      error.value = null;
      await apiClient.removeTeamMember(teamId, userId);
      
      // Refresh team data to get updated members
      await fetchTeam(teamId);
    } catch (err: any) {
      error.value = err.response?.data?.detail || '移除成员失败';
      console.error('Failed to remove team member:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function fetchTeamSchedules(teamId: number) {
    try {
      loading.value = true;
      error.value = null;
      const events = await apiClient.getTeamSchedules(teamId);
      teamEvents.value = events;
      return events;
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取团队课表失败';
      console.error('Failed to fetch team schedules:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Admin functions
  async function fetchAllTeams() {
    try {
      loading.value = true;
      error.value = null;
      const data = await apiClient.getAllTeamsAdmin();
      allTeams.value = data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取所有团队失败';
      console.error('Failed to fetch all teams:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function fetchUsers() {
    try {
      loading.value = true;
      error.value = null;
      const data = await apiClient.getAllUsersAdmin();
      userList.value = data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取用户列表失败';
      console.error('Failed to fetch users:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  function clearError() {
    error.value = null;
  }

  function clearCurrentTeam() {
    currentTeam.value = null;
    teamEvents.value = [];
  }

  // Reset store state
  function $reset() {
    teams.value = [];
    currentTeam.value = null;
    teamEvents.value = [];
    allTeams.value = [];
    userList.value = [];
    loading.value = false;
    error.value = null;
  }

  return {
    // State
    teams,
    currentTeam,
    teamEvents,
    allTeams,
    userList,
    loading,
    error,
    
    // Getters
    getTeamById,
    isTeamCreator,
    isTeamMember,
    allClasses,
    allGrades,
    
    // Actions
    fetchMyTeams,
    fetchTeam,
    createTeam,
    updateTeam,
    deleteTeam,
    joinTeam,
    leaveTeam,
    addTeamMember,
    removeTeamMember,
    fetchTeamSchedules,
    
    // Admin actions
    fetchAllTeams,
    fetchUsers,
    
    clearError,
    clearCurrentTeam,
    $reset
  };
});