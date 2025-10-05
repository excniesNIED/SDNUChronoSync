<template>
  <footer class="bg-white border-t border-gray-200 mt-auto">
    <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <div class="flex flex-col items-center justify-center space-y-2 text-center">
        <!-- 版权信息和组织 -->
        <div class="flex flex-wrap items-center justify-center gap-2 text-sm text-gray-600">
          <span>© {{ currentYear }}</span>
          <a 
            href="https://hevspecu.hxcn.space" 
            target="_blank" 
            rel="noopener noreferrer"
            class="text-indigo-600 hover:text-indigo-800 transition-colors font-medium"
          >
            天空之镜 (HevSpecu)
          </a>
        </div>
        
        <!-- 技术栈信息 -->
        <div class="flex items-center gap-2 text-xs text-gray-500">
          <span>由</span>
          <a 
            href="https://astro.build" 
            target="_blank" 
            rel="noopener noreferrer"
            class="text-indigo-500 hover:text-indigo-700 transition-colors font-medium"
          >
            Astro
          </a>
          <span>和</span>
          <a 
            href="https://vuejs.org" 
            target="_blank" 
            rel="noopener noreferrer"
            class="text-indigo-500 hover:text-indigo-700 transition-colors font-medium"
          >
            Vue.js
          </a>
          <span>强力驱动</span>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const currentYear = computed(() => new Date().getFullYear());
</script>

<style scoped>
/* 额外的样式可以在这里添加 */
</style>

