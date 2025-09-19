<template>
  <div class="p-6 space-y-6">
    <div>
      <h3 class="text-lg font-medium text-gray-900 mb-4">筛选条件</h3>
    </div>

    <!-- Date Range -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        日期范围
      </label>
      <div class="space-y-3">
        <div>
          <label class="block text-xs text-gray-500 mb-1">开始日期</label>
          <input
            :value="filterState.dateRange.start"
            @input="updateDateRange('start', $event.target.value)"
            type="date"
            class="block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm"
          />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">结束日期</label>
          <input
            :value="filterState.dateRange.end"
            @input="updateDateRange('end', $event.target.value)"
            type="date"
            class="block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm"
          />
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
            
            <div class="p-2">
              <button
                @click="selectAllUsers"
                class="w-full text-left px-2 py-1 text-sm text-primary-600 hover:bg-primary-50 rounded"
              >
                全选
              </button>
              <button
                @click="clearAllUsers"
                class="w-full text-left px-2 py-1 text-sm text-gray-600 hover:bg-gray-50 rounded"
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
              <span class="block truncate font-normal">
                {{ user.full_name }}
              </span>
              <span class="block truncate text-xs text-gray-500">
                {{ user.class_name }} - {{ user.student_id }}
              </span>
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

    <!-- Class Filter -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        班级
      </label>
      <select
        :value="filterState.className"
        @change="updateFilter({ className: $event.target.value })"
        class="block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm"
      >
        <option value="">全部班级</option>
        <option v-for="className in allClasses" :key="className" :value="className">
          {{ className }}
        </option>
      </select>
    </div>

    <!-- Grade Filter -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        年级
      </label>
      <select
        :value="filterState.grade"
        @change="updateFilter({ grade: $event.target.value })"
        class="block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm"
      >
        <option value="">全部年级</option>
        <option v-for="grade in allGrades" :key="grade" :value="grade">
          {{ grade }}级
        </option>
      </select>
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

    <!-- Apply Button -->
    <div>
      <button
        @click="$emit('apply-filter')"
        class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        应用筛选
      </button>
    </div>

    <!-- Clear Button -->
    <div>
      <button
        @click="clearAllFilters"
        class="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        清空筛选
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { CheckIcon, ChevronUpDownIcon } from '@heroicons/vue/24/outline';
import type { User, FilterState } from '@/types';

interface Props {
  users: User[];
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

const selectedUsersText = computed(() => {
  const count = props.filterState.selectedUserIds.length;
  if (count === 0) return '选择成员';
  if (count === 1) {
    const user = props.users.find(u => u.id === props.filterState.selectedUserIds[0]);
    return user?.full_name || '1个成员';
  }
  return `${count}个成员`;
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

function clearAllFilters() {
  const today = new Date();
  const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
  
  updateFilter({
    dateRange: {
      start: today.toISOString().split('T')[0],
      end: nextWeek.toISOString().split('T')[0],
    },
    selectedUserIds: [],
    className: '',
    grade: '',
    nameKeyword: '',
    eventKeyword: '',
  });
}

// Close dropdown when clicking outside
function handleClickOutside(event: Event) {
  const target = event.target as Element;
  if (!target.closest('.relative')) {
    userDropdownOpen.value = false;
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>
