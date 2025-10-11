<template>
  <div class="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
    <!-- Sidebar component -->
    <div class="flex grow flex-col gap-y-5 overflow-y-auto bg-white px-6 pb-4 shadow-sm ring-1 ring-gray-900/5">
      <!-- Logo -->
      <div class="flex h-16 shrink-0 items-center justify-between">
        <div class="flex items-center gap-2">
          <img src="/favicon.svg" alt="时序同笺" class="h-8 w-8" />
          <h1 class="text-2xl font-bold text-primary-600">时序同笺</h1>
        </div>
        <!-- Theme Toggle -->
        <button
          @click="themeStore.toggleTheme()"
          class="p-2 rounded-md text-gray-400 hover:text-primary-600 hover:bg-primary-50 transition-colors"
          :title="themeStore.isDark() ? '切换到浅色模式' : '切换到深色模式'"
        >
          <SunIcon v-if="themeStore.isDark()" class="h-5 w-5" aria-hidden="true" />
          <MoonIcon v-else class="h-5 w-5" aria-hidden="true" />
        </button>
      </div>

      <!-- Navigation -->
      <nav class="flex flex-1 flex-col">
        <ul role="list" class="flex flex-1 flex-col gap-y-7">
          <li>
            <ul role="list" class="-mx-2 space-y-1">
              <li v-for="item in navigation" :key="item.name">
                <a
                  :href="item.href"
                  :target="item.external ? '_blank' : undefined"
                  :rel="item.external ? 'noopener noreferrer' : undefined"
                  :class="[
                    item.current
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:text-primary-700 hover:bg-primary-50',
                    'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold transition-colors'
                  ]"
                >
                  <component
                    :is="item.icon"
                    :class="[
                      item.current ? 'text-primary-700' : 'text-gray-400 group-hover:text-primary-700',
                      'h-6 w-6 shrink-0'
                    ]"
                    aria-hidden="true"
                  />
                  {{ item.name }}
                </a>
              </li>
            </ul>
          </li>

          <!-- Admin Section -->
          <li v-if="authStore.isAdmin">
            <div class="text-xs font-semibold leading-6 text-gray-400">管理员功能</div>
            <ul role="list" class="-mx-2 mt-2 space-y-1">
              <li v-for="item in adminNavigation" :key="item.name">
                <a
                  :href="item.href"
                  :class="[
                    item.current
                      ? 'bg-red-50 text-red-700'
                      : 'text-gray-700 hover:text-red-700 hover:bg-red-50',
                    'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold transition-colors'
                  ]"
                >
                  <component
                    :is="item.icon"
                    :class="[
                      item.current ? 'text-red-700' : 'text-gray-400 group-hover:text-red-700',
                      'h-6 w-6 shrink-0'
                    ]"
                    aria-hidden="true"
                  />
                  {{ item.name }}
                </a>
              </li>
            </ul>
          </li>

          <!-- User Info -->
          <li class="mt-auto">
            <div class="mb-3 px-2">
              <div class="flex items-center gap-x-3 py-2">
                <UserAvatar 
                  :user="authStore.user" 
                  size="md" 
                  :clickable="true"
                  @click="goToProfile"
                />
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-900 truncate">
                    {{ authStore.user?.full_name || '用户' }}
                  </p>
                  <p class="text-xs text-gray-500 truncate">
                    {{ authStore.user?.class_name || '' }}
                  </p>
                </div>
              </div>
            </div>
          </li>

          <!-- Logout -->
          <li>
            <button
              @click="handleLogout"
              class="group flex w-full gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold text-gray-700 hover:bg-red-50 hover:text-red-700 transition-colors"
            >
              <ArrowRightOnRectangleIcon class="h-6 w-6 shrink-0 text-gray-400 group-hover:text-red-700" />
              退出登录
            </button>
          </li>
        </ul>
      </nav>
    </div>
  </div>

  <!-- Mobile menu -->
  <div class="lg:hidden">
    <!-- Mobile menu button -->
    <div class="fixed top-0 left-0 right-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6">
      <button
        @click="mobileMenuOpen = true"
        type="button"
        class="-m-2.5 p-2.5 text-gray-700 lg:hidden"
      >
        <span class="sr-only">打开侧边栏</span>
        <Bars3Icon class="h-6 w-6" aria-hidden="true" />
      </button>

      <div class="flex flex-1 gap-x-2 sm:gap-x-4 self-stretch lg:gap-x-6">
        <div class="flex flex-1 items-center min-w-0">
          <div class="flex items-center gap-2">
            <img src="/favicon.svg" alt="时序同笺" class="h-6 w-6 flex-shrink-0" />
            <h1 class="text-base sm:text-lg font-semibold text-gray-900 truncate">时序同笺</h1>
          </div>
        </div>
        
        <!-- Mobile theme toggle -->
        <div class="flex items-center gap-x-2 flex-shrink-0">
          <button
            @click="themeStore.toggleTheme()"
            class="p-1.5 sm:p-2 rounded-md text-gray-400 hover:text-primary-600 hover:bg-primary-50 transition-colors flex-shrink-0"
            :title="themeStore.isDark() ? '切换到浅色模式' : '切换到深色模式'"
          >
            <SunIcon v-if="themeStore.isDark()" class="h-5 w-5" aria-hidden="true" />
            <MoonIcon v-else class="h-5 w-5" aria-hidden="true" />
          </button>
          
          <!-- Mobile user avatar -->
          <div class="flex-shrink-0">
            <UserAvatar 
              :user="authStore.user" 
              size="sm" 
              :clickable="true"
              @click="goToProfile"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile drawer -->
    <MobileDrawer
      :is-open="mobileMenuOpen"
      @close="mobileMenuOpen = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useThemeStore } from '@/stores/theme';
import MobileDrawer from './MobileDrawer.vue';
import UserAvatar from './UserAvatar.vue';
import {
  Bars3Icon,
  CalendarIcon,
  UsersIcon,
  UserGroupIcon,
  Cog6ToothIcon,
  UserIcon,
  ArrowRightOnRectangleIcon,
  InformationCircleIcon,
  AcademicCapIcon,
  SunIcon,
  MoonIcon,
} from '@heroicons/vue/24/outline';

const authStore = useAuthStore();
const themeStore = useThemeStore();
const mobileMenuOpen = ref(false);

// Get current path to determine active navigation item
const currentPath = ref('');

onMounted(async () => {
  currentPath.value = window.location.pathname;
  
  // Initialize auth store to ensure user data is loaded
  await authStore.initialize();
});

const navigation = computed(() => [
  {
    name: '我的课表',
    href: '/dashboard/my-schedule',
    icon: CalendarIcon,
    current: currentPath.value === '/dashboard/my-schedule',
  },
  {
    name: '我的团队',
    href: '/dashboard/my-teams',
    icon: UserGroupIcon,
    current: currentPath.value === '/dashboard/my-teams',
  },
  {
    name: '团队视图',
    href: '/dashboard/team-view',
    icon: UsersIcon,
    current: currentPath.value.startsWith('/dashboard/team-view'),
  },
  {
    name: '个人中心',
    href: '/dashboard/profile',
    icon: UserIcon,
    current: currentPath.value === '/dashboard/profile',
  },
  {
    name: '使用教程',
    href: 'https://hs.cnies.org/archives/chronosync-user-guide',
    icon: AcademicCapIcon,
    current: false,
    external: true,
  },
  {
    name: '关于',
    href: 'https://hs.cnies.org/archives/chronosync',
    icon: InformationCircleIcon,
    current: false,
    external: true,
  },
]);

const adminNavigation = computed(() => [
  {
    name: '用户管理',
    href: '/dashboard/admin/user-management',
    icon: UsersIcon,
    current: currentPath.value === '/dashboard/admin/user-management',
  },
  {
    name: '团队管理',
    href: '/dashboard/admin/team-management',
    icon: UserGroupIcon,
    current: currentPath.value === '/dashboard/admin/team-management',
  },
  {
    name: '课表管理',
    href: '/dashboard/admin/schedule-management',
    icon: Cog6ToothIcon,
    current: currentPath.value === '/dashboard/admin/schedule-management',
  },
  {
    name: '系统设置',
    href: '/dashboard/admin/system-settings',
    icon: Cog6ToothIcon,
    current: currentPath.value === '/dashboard/admin/system-settings',
  },
]);

async function handleLogout() {
  await authStore.logout();
  // Redirect to login page after logout
  window.location.href = '/login';
}

function goToProfile() {
  window.location.href = '/dashboard/profile';
}
</script>
