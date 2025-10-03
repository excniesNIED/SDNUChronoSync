<template>
  <div 
    :class="[
      'relative inline-flex items-center justify-center rounded-full overflow-hidden bg-gradient-to-br',
      sizeClasses,
      clickable ? 'cursor-pointer hover:opacity-80 transition-opacity' : '',
      colorClasses
    ]"
    :title="user?.full_name || '用户'"
    @click="handleClick"
  >
    <!-- 自定义头像 -->
    <img
      v-if="user?.avatar_url"
      :src="getAvatarUrl(user.avatar_url)"
      :alt="user.full_name || '用户头像'"
      class="w-full h-full object-cover"
      @error="handleImageError"
    />
    
    <!-- 默认头像（用户名首字母） -->
    <span
      v-else
      :class="[
        'font-medium text-white select-none',
        textSizeClasses
      ]"
    >
      {{ getInitials(user?.full_name) }}
    </span>
    
    <!-- 在线状态指示器 -->
    <div
      v-if="showOnlineStatus"
      :class="[
        'absolute bottom-0 right-0 rounded-full border-2 border-white',
        size === 'xs' ? 'w-2 h-2' : size === 'sm' ? 'w-3 h-3' : 'w-4 h-4',
        isOnline ? 'bg-green-400' : 'bg-gray-400'
      ]"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import type { User } from '@/types';

interface Props {
  user?: User | null;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  clickable?: boolean;
  showOnlineStatus?: boolean;
  isOnline?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  clickable: false,
  showOnlineStatus: false,
  isOnline: false
});

const emit = defineEmits<{
  click: [user: User | null | undefined];
}>();

const imageError = ref(false);

const sizeClasses = computed(() => {
  const sizes = {
    xs: 'w-6 h-6',
    sm: 'w-8 h-8', 
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };
  return sizes[props.size];
});

const textSizeClasses = computed(() => {
  const sizes = {
    xs: 'text-xs',
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
    xl: 'text-xl'
  };
  return sizes[props.size];
});

// 根据用户名生成颜色
const colorClasses = computed(() => {
  if (props.user?.avatar_url && !imageError.value) {
    return 'bg-gray-100';
  }
  
  // 根据用户名的hash值生成颜色
  const colors = [
    'from-blue-400 to-blue-600',
    'from-green-400 to-green-600', 
    'from-purple-400 to-purple-600',
    'from-pink-400 to-pink-600',
    'from-indigo-400 to-indigo-600',
    'from-yellow-400 to-yellow-600',
    'from-red-400 to-red-600',
    'from-teal-400 to-teal-600'
  ];
  
  const name = props.user?.full_name || 'User';
  const hash = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return colors[hash % colors.length];
});

const getInitials = (name?: string): string => {
  if (!name) return 'U';
  
  // 对于中文名字，取前两个字符
  if (/[\u4e00-\u9fa5]/.test(name)) {
    return name.slice(0, 2);
  }
  
  // 对于英文名字，取首字母
  return name
    .split(' ')
    .map(word => word.charAt(0).toUpperCase())
    .slice(0, 2)
    .join('');
};

const getAvatarUrl = (avatarUrl: string): string => {
  // 如果是完整的URL，直接返回
  if (avatarUrl.startsWith('http://') || avatarUrl.startsWith('https://')) {
    return avatarUrl;
  }
  
  // 如果是相对路径，添加API基础URL
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  return `${apiBaseUrl}${avatarUrl}`;
};

const handleImageError = () => {
  imageError.value = true;
};

const handleClick = () => {
  if (props.clickable) {
    emit('click', props.user);
  }
};
</script>
