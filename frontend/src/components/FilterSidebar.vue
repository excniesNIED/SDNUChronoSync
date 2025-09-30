<template>
  <div class="p-4 md:p-6 space-y-5">
    <div>
      <h3 class="text-base md:text-lg font-medium text-gray-900 mb-3">筛选条件</h3>
    </div>

    <!-- Date Range -->
    <div>
      <div class="flex items-center justify-between mb-2">
        <label class="block text-sm font-medium text-gray-700">
          日期范围
        </label>
      </div>
      <div class="space-y-3">
        <div>
          <label class="block text-xs text-gray-500 mb-1">开始日期</label>
          <input
            :value="filterState.dateRange.start"
            @input="updateDateRange('start', $event.target.value)"
            type="date"
            class="block w-full rounded-md border-0 py-1.5 px-3 text-sm text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600"
          />
          <p v-if="filterState.dateRange.start" class="mt-1 text-xs text-primary-600">
            已选择: {{ formatDatePreview(filterState.dateRange.start) }}
          </p>
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">结束日期</label>
          <input
            :value="filterState.dateRange.end"
            @input="updateDateRange('end', $event.target.value)"
            type="date"
            class="block w-full rounded-md border-0 py-1.5 px-3 text-sm text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600"
          />
          <p v-if="filterState.dateRange.end" class="mt-1 text-xs text-primary-600">
            已选择: {{ formatDatePreview(filterState.dateRange.end) }}
          </p>
        </div>
      </div>
    </div>

    <!-- User Selection -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        选择成员
      </label>
      <div class="relative">
        <button
          @click="userDropdownOpen = !userDropdownOpen"
          class="relative w-full cursor-default rounded-md bg-white py-1.5 pl-3 pr-10 text-left text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-600 sm:text-sm"
        >
          <span class="block truncate">
            {{ selectedUsersText }}
          </span>
          <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
            <ChevronUpDownIcon class="h-5 w-5 text-gray-400" />
          </span>
        </button>

        <transition
          leave-active-class="transition ease-in duration-100"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0"
        >
          <div
            v-if="userDropdownOpen"
            class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm"
          >
            <div class="sticky top-0 bg-white p-2 border-b">
              <input
                v-model="userSearchQuery"
                type="text"
                placeholder="搜索成员..."
                class="w-full rounded-md border-0 py-1 px-2 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm"
              />
            </div>
            
            <div class="flex items-center justify-end gap-2 px-3 py-2 border-b border-gray-100 bg-gray-50">
              <button
                @click="selectAllUsers"
                class="px-2 py-1 text-xs font-medium text-primary-600 hover:bg-primary-100 rounded transition-colors"
              >
                全选
              </button>
              <button
                @click="clearAllUsers"
                class="px-2 py-1 text-xs font-medium text-gray-600 hover:bg-gray-200 rounded transition-colors"
              >
                清空
              </button>
            </div>

            <div
              v-for="user in filteredUsers"
              :key="user.id"
              @click="toggleUser(user.id)"
              class="relative cursor-pointer select-none py-2 pl-8 pr-4 hover:bg-gray-50"
            >
              <div class="flex items-center gap-3">
                <UserAvatar :user="user" size="xs" />
                <div class="flex-1 min-w-0">
                  <span class="block truncate font-normal">
                    {{ user.full_name }}
                  </span>
                  <span class="block truncate text-xs text-gray-500">
                    {{ user.class_name }} - {{ user.student_id }}
                  </span>
                </div>
              </div>
              <span
                v-if="filterState.selectedUserIds.includes(user.id)"
                class="absolute inset-y-0 left-0 flex items-center pl-2 text-primary-600"
              >
                <CheckIcon class="h-4 w-4" />
              </span>
            </div>

            <div v-if="filteredUsers.length === 0" class="py-4 px-4 text-sm text-gray-500 text-center">
              没有找到匹配的成员
            </div>
          </div>
        </transition>
      </div>
    </div>

    <!-- Team Filter -->
    <div v-if="teams && teams.length > 0">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        按团队筛选
      </label>
      <div class="relative">
        <button
          @click="teamDropdownOpen = !teamDropdownOpen"
          class="relative w-full cursor-default rounded-md bg-white py-1.5 pl-3 pr-10 text-left text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-600 sm:text-sm"
        >
          <span class="block truncate">
            {{ selectedTeamsText }}
          </span>
          <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
            <ChevronUpDownIcon class="h-5 w-5 text-gray-400" />
          </span>
        </button>

        <transition
          leave-active-class="transition ease-in duration-100"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0"
        >
          <div
            v-if="teamDropdownOpen"
            class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm"
          >
            <div class="flex items-center justify-end gap-2 px-3 py-2 border-b border-gray-100 bg-gray-50">
              <button
                @click="selectAllTeams"
                class="px-2 py-1 text-xs font-medium text-primary-600 hover:bg-primary-100 rounded transition-colors"
              >
                全选
              </button>
              <button
                @click="clearAllTeams"
                class="px-2 py-1 text-xs font-medium text-gray-600 hover:bg-gray-200 rounded transition-colors"
              >
                清空
              </button>
            </div>

            <div
              v-for="team in teams"
              :key="team.id"
              @click="toggleTeam(team.id)"
              class="relative cursor-pointer select-none py-2 pl-8 pr-4 hover:bg-gray-50"
            >
              <span class="block truncate font-normal">
                {{ team.name }}
              </span>
              <span class="block truncate text-xs text-gray-500">
                {{ team.members?.length || 0 }} 名成员 · {{ team.team_code }}
              </span>
              <span
                v-if="filterState.selectedTeamIds.includes(team.id)"
                class="absolute inset-y-0 left-0 flex items-center pl-2 text-primary-600"
              >
                <CheckIcon class="h-4 w-4" />
              </span>
            </div>

            <div v-if="teams.length === 0" class="py-4 px-4 text-sm text-gray-500 text-center">
              没有找到团队
            </div>
          </div>
        </transition>
      </div>
    </div>

    <!-- Class Filter -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        选择班级
      </label>
      <div class="relative">
        <button
          @click="classDropdownOpen = !classDropdownOpen"
          class="relative w-full cursor-default rounded-md bg-white py-1.5 pl-3 pr-10 text-left text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-600 sm:text-sm"
        >
          <span class="block truncate">
            {{ selectedClassesText }}
          </span>
          <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
            <ChevronUpDownIcon class="h-5 w-5 text-gray-400" />
          </span>
        </button>

        <transition
          leave-active-class="transition ease-in duration-100"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0"
        >
          <div
            v-if="classDropdownOpen"
            class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm"
          >
            <div class="flex items-center justify-end gap-2 px-3 py-2 border-b border-gray-100 bg-gray-50">
              <button
                @click="selectAllClasses"
                class="px-2 py-1 text-xs font-medium text-primary-600 hover:bg-primary-100 rounded transition-colors"
              >
                全选
              </button>
              <button
                @click="clearAllClasses"
                class="px-2 py-1 text-xs font-medium text-gray-600 hover:bg-gray-200 rounded transition-colors"
              >
                清空
              </button>
            </div>

            <div
              v-for="className in allClasses"
              :key="className"
              @click="toggleClass(className)"
              class="relative cursor-pointer select-none py-2 pl-8 pr-4 hover:bg-gray-50"
            >
              <span class="block truncate font-normal">
                {{ className }}
              </span>
              <span
                v-if="filterState.selectedClassNames.includes(className)"
                class="absolute inset-y-0 left-0 flex items-center pl-2 text-primary-600"
              >
                <CheckIcon class="h-4 w-4" />
              </span>
            </div>

            <div v-if="allClasses.length === 0" class="py-4 px-4 text-sm text-gray-500 text-center">
              没有找到班级
            </div>
          </div>
        </transition>
      </div>
    </div>

    <!-- Grade Filter -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        选择年级
      </label>
      <div class="relative">
        <button
          @click="gradeDropdownOpen = !gradeDropdownOpen"
          class="relative w-full cursor-default rounded-md bg-white py-1.5 pl-3 pr-10 text-left text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-600 sm:text-sm"
        >
          <span class="block truncate">
            {{ selectedGradesText }}
          </span>
          <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
            <ChevronUpDownIcon class="h-5 w-5 text-gray-400" />
          </span>
        </button>

        <transition
          leave-active-class="transition ease-in duration-100"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0"
        >
          <div
            v-if="gradeDropdownOpen"
            class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm"
          >
            <div class="flex items-center justify-end gap-2 px-3 py-2 border-b border-gray-100 bg-gray-50">
              <button
                @click="selectAllGrades"
                class="px-2 py-1 text-xs font-medium text-primary-600 hover:bg-primary-100 rounded transition-colors"
              >
                全选
              </button>
              <button
                @click="clearAllGrades"
                class="px-2 py-1 text-xs font-medium text-gray-600 hover:bg-gray-200 rounded transition-colors"
              >
                清空
              </button>
            </div>

            <div
              v-for="grade in allGrades"
              :key="grade"
              @click="toggleGrade(grade)"
              class="relative cursor-pointer select-none py-2 pl-8 pr-4 hover:bg-gray-50"
            >
              <span class="block truncate font-normal">
                {{ grade }}级
              </span>
              <span
                v-if="filterState.selectedGrades.includes(grade)"
                class="absolute inset-y-0 left-0 flex items-center pl-2 text-primary-600"
              >
                <CheckIcon class="h-4 w-4" />
              </span>
            </div>

            <div v-if="allGrades.length === 0" class="py-4 px-4 text-sm text-gray-500 text-center">
              没有找到年级
            </div>
          </div>
        </transition>
      </div>
    </div>

    <!-- Name Search -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        姓名关键词
      </label>
      <input
        :value="filterState.nameKeyword"
        @input="updateFilter({ nameKeyword: $event.target.value })"
        type="text"
        placeholder="输入姓名关键词"
        class="block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm"
      />
    </div>

    <!-- Event Search -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        课程关键词
      </label>
      <input
        :value="filterState.eventKeyword"
        @input="updateFilter({ eventKeyword: $event.target.value })"
        type="text"
        placeholder="输入课程关键词"
        class="block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm"
      />
    </div>

    <!-- Action Buttons -->
    <div class="flex gap-3 pt-2">
      <button
        @click="$emit('apply-filter')"
        class="flex-1 flex justify-center items-center gap-1.5 py-2.5 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
      >
        <CheckIcon class="h-4 w-4" />
        应用筛选
      </button>
      <button
        @click="clearAllFilters"
        class="px-4 py-2.5 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
        title="清空所有筛选"
      >
        <XMarkIcon class="h-4 w-4" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { CheckIcon, ChevronUpDownIcon, XMarkIcon } from '@heroicons/vue/24/outline';
import { formatDisplayDate } from '@/utils/date';
import UserAvatar from './UserAvatar.vue';
import type { User, FilterState, Team } from '@/types';

interface Props {
  users: User[];
  teams?: Team[];  // 新增团队数据
  filterState: FilterState;
  allClasses: string[];
  allGrades: string[];
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'update-filter': [filter: Partial<FilterState>];
  'apply-filter': [];
}>();

const userDropdownOpen = ref(false);
const userSearchQuery = ref('');
const teamDropdownOpen = ref(false);
const classDropdownOpen = ref(false);
const gradeDropdownOpen = ref(false);

const selectedUsersText = computed(() => {
  const count = props.filterState.selectedUserIds.length;
  if (count === 0) return '选择成员';
  if (count === 1) {
    const user = props.users.find(u => u.id === props.filterState.selectedUserIds[0]);
    return user?.full_name || '1个成员';
  }
  return `${count}个成员`;
});

const selectedTeamsText = computed(() => {
  const count = props.filterState.selectedTeamIds.length;
  if (count === 0) return '选择团队';
  if (count === 1) {
    const team = props.teams?.find(t => t.id === props.filterState.selectedTeamIds[0]);
    return team?.name || '1个团队';
  }
  return `${count}个团队`;
});

const selectedClassesText = computed(() => {
  const count = props.filterState.selectedClassNames.length;
  if (count === 0) return '选择班级';
  if (count === 1) {
    return props.filterState.selectedClassNames[0];
  }
  return `${count}个班级`;
});

const selectedGradesText = computed(() => {
  const count = props.filterState.selectedGrades.length;
  if (count === 0) return '选择年级';
  if (count === 1) {
    return `${props.filterState.selectedGrades[0]}级`;
  }
  return `${count}个年级`;
});

const filteredUsers = computed(() => {
  if (!userSearchQuery.value.trim()) {
    return props.users;
  }
  
  const query = userSearchQuery.value.toLowerCase();
  return props.users.filter(user => 
    user.full_name.toLowerCase().includes(query) ||
    user.student_id.toLowerCase().includes(query) ||
    user.class_name.toLowerCase().includes(query)
  );
});

function updateFilter(newFilter: Partial<FilterState>) {
  emit('update-filter', newFilter);
}

function updateDateRange(type: 'start' | 'end', value: string) {
  const newDateRange = { ...props.filterState.dateRange };
  newDateRange[type] = value;
  updateFilter({ dateRange: newDateRange });
}

function toggleUser(userId: number) {
  const currentIds = [...props.filterState.selectedUserIds];
  const index = currentIds.indexOf(userId);
  
  if (index > -1) {
    currentIds.splice(index, 1);
  } else {
    currentIds.push(userId);
  }
  
  updateFilter({ selectedUserIds: currentIds });
}

function selectAllUsers() {
  const allUserIds = props.users.map(user => user.id);
  updateFilter({ selectedUserIds: allUserIds });
}

function clearAllUsers() {
  updateFilter({ selectedUserIds: [] });
}

function toggleTeam(teamId: number) {
  const currentIds = [...props.filterState.selectedTeamIds];
  const index = currentIds.indexOf(teamId);
  
  if (index > -1) {
    currentIds.splice(index, 1);
  } else {
    currentIds.push(teamId);
  }
  
  updateFilter({ selectedTeamIds: currentIds });
}

function selectAllTeams() {
  const allTeamIds = props.teams?.map(team => team.id) || [];
  updateFilter({ selectedTeamIds: allTeamIds });
}

function clearAllTeams() {
  updateFilter({ selectedTeamIds: [] });
}

function toggleClass(className: string) {
  const currentClasses = [...props.filterState.selectedClassNames];
  const index = currentClasses.indexOf(className);
  
  if (index > -1) {
    currentClasses.splice(index, 1);
  } else {
    currentClasses.push(className);
  }
  
  updateFilter({ selectedClassNames: currentClasses });
}

function selectAllClasses() {
  updateFilter({ selectedClassNames: [...props.allClasses] });
}

function clearAllClasses() {
  updateFilter({ selectedClassNames: [] });
}

function toggleGrade(grade: string) {
  const currentGrades = [...props.filterState.selectedGrades];
  const index = currentGrades.indexOf(grade);
  
  if (index > -1) {
    currentGrades.splice(index, 1);
  } else {
    currentGrades.push(grade);
  }
  
  updateFilter({ selectedGrades: currentGrades });
}

function selectAllGrades() {
  updateFilter({ selectedGrades: [...props.allGrades] });
}

function clearAllGrades() {
  updateFilter({ selectedGrades: [] });
}

function clearAllFilters() {
  const today = new Date();
  const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
  
  updateFilter({
    dateRange: {
      start: today.toISOString().split('T')[0],
      end: nextWeek.toISOString().split('T')[0],
    },
    selectedUserIds: [],
    selectedTeamIds: [],
    selectedClassNames: [],
    selectedGrades: [],
    nameKeyword: '',
    eventKeyword: '',
  });
}

// 格式化日期预览（显示中文格式）
function formatDatePreview(dateString: string): string {
  if (!dateString) return '';
  try {
    return formatDisplayDate(dateString);
  } catch (error) {
    return dateString;
  }
}

// Close dropdown when clicking outside
function handleClickOutside(event: Event) {
  const target = event.target as Element;
  if (!target.closest('.relative')) {
    userDropdownOpen.value = false;
    teamDropdownOpen.value = false;
    classDropdownOpen.value = false;
    gradeDropdownOpen.value = false;
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>
