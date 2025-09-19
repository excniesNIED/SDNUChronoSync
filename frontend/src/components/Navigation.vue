<template>
  <div class="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
    <!-- Sidebar component -->
    <div class="flex grow flex-col gap-y-5 overflow-y-auto bg-white px-6 pb-4 shadow-sm ring-1 ring-gray-900/5">
      <!-- Logo -->
      <div class="flex h-16 shrink-0 items-center">
        <h1 class="text-2xl font-bold text-primary-600">课表管理</h1>
      </div>

      <!-- Navigation -->
      <nav class="flex flex-1 flex-col">
        <ul role="list" class="flex flex-1 flex-col gap-y-7">
          <li>
            <ul role="list" class="-mx-2 space-y-1">
              <li v-for="item in navigation" :key="item.name">
                <a
                  :href="item.href"
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

          <!-- User info and logout -->
          <li class="mt-auto">
            <div class="flex items-center gap-x-4 px-2 py-3 text-sm font-semibold leading-6 text-gray-900">
              <div class="flex h-8 w-8 items-center justify-center rounded-full bg-primary-100">
                <UserIcon class="h-5 w-5 text-primary-600" />
              </div>
              <div class="flex-1">
                <div class="text-sm font-medium text-gray-900">{{ authStore.currentUser?.full_name }}</div>
                <div class="text-xs text-gray-500">{{ authStore.currentUser?.class_name }}</div>
              </div>
            </div>
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
    <div class="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6">
      <button
        @click="mobileMenuOpen = true"
        type="button"
        class="-m-2.5 p-2.5 text-gray-700 lg:hidden"
      >
        <span class="sr-only">打开侧边栏</span>
        <Bars3Icon class="h-6 w-6" aria-hidden="true" />
      </button>

      <div class="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
        <div class="flex flex-1 items-center">
          <h1 class="text-lg font-semibold text-gray-900">课表管理</h1>
        </div>
      </div>
    </div>

    <!-- Mobile sidebar overlay -->
    <TransitionRoot as="template" :show="mobileMenuOpen">
      <Dialog as="div" class="relative z-50 lg:hidden" @close="mobileMenuOpen = false">
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
                  <button type="button" class="-m-2.5 p-2.5" @click="mobileMenuOpen = false">
                    <span class="sr-only">关闭侧边栏</span>
                    <XMarkIcon class="h-6 w-6 text-white" aria-hidden="true" />
                  </button>
                </div>
              </TransitionChild>

              <!-- Mobile navigation content (same as desktop) -->
              <div class="flex grow flex-col gap-y-5 overflow-y-auto bg-white px-6 pb-4">
                <div class="flex h-16 shrink-0 items-center">
                  <h1 class="text-2xl font-bold text-primary-600">课表管理</h1>
                </div>
                <!-- Same navigation content as desktop -->
                <nav class="flex flex-1 flex-col">
                  <!-- Navigation items... (same as above) -->
                </nav>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </Dialog>
    </TransitionRoot>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import {
  Dialog,
  DialogPanel,
  TransitionChild,
  TransitionRoot,
} from '@headlessui/vue';
import {
  Bars3Icon,
  CalendarIcon,
  UsersIcon,
  UserGroupIcon,
  Cog6ToothIcon,
  UserIcon,
  ArrowRightOnRectangleIcon,
  XMarkIcon,
} from '@heroicons/vue/24/outline';

const authStore = useAuthStore();
const mobileMenuOpen = ref(false);

// Get current path to determine active navigation item
const currentPath = ref('');

onMounted(() => {
  currentPath.value = window.location.pathname;
});

const navigation = computed(() => [
  {
    name: '我的课表',
    href: '/dashboard/my-schedule',
    icon: CalendarIcon,
    current: currentPath.value === '/dashboard/my-schedule',
  },
  {
    name: '团队视图',
    href: '/dashboard/team-view',
    icon: UserGroupIcon,
    current: currentPath.value === '/dashboard/team-view',
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
    name: '课表管理',
    href: '/dashboard/admin/schedule-management',
    icon: Cog6ToothIcon,
    current: currentPath.value === '/dashboard/admin/schedule-management',
  },
]);

async function handleLogout() {
  await authStore.logout();
}
</script>
