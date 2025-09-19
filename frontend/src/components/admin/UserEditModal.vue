<template>
  <TransitionRoot as="template" :show="isOpen">
    <Dialog as="div" class="relative z-50" @close="$emit('close')">
      <TransitionChild
        as="template"
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
      </TransitionChild>

      <div class="fixed inset-0 z-10 overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild
            as="template"
            enter="ease-out duration-300"
            enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          >
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <form @submit.prevent="handleSubmit">
                <div>
                  <div class="text-center">
                    <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">
                      {{ isEditMode ? '编辑用户' : '添加用户' }}
                    </DialogTitle>
                  </div>

                  <div class="mt-6 space-y-4">
                    <!-- Student ID -->
                    <div>
                      <label for="student_id" class="block text-sm font-medium leading-6 text-gray-900">
                        学号 <span class="text-red-500">*</span>
                      </label>
                      <input
                        id="student_id"
                        v-model="form.student_id"
                        type="text"
                        required
                        :disabled="isEditMode"
                        class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 disabled:bg-gray-50 disabled:text-gray-500"
                        placeholder="请输入学号"
                      />
                      <p v-if="isEditMode" class="mt-1 text-xs text-gray-500">
                        编辑模式下学号不可修改
                      </p>
                    </div>

                    <!-- Full Name -->
                    <div>
                      <label for="full_name" class="block text-sm font-medium leading-6 text-gray-900">
                        姓名 <span class="text-red-500">*</span>
                      </label>
                      <input
                        id="full_name"
                        v-model="form.full_name"
                        type="text"
                        required
                        class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                        placeholder="请输入姓名"
                      />
                    </div>

                    <!-- Class Name -->
                    <div>
                      <label for="class_name" class="block text-sm font-medium leading-6 text-gray-900">
                        班级 <span class="text-red-500">*</span>
                      </label>
                      <input
                        id="class_name"
                        v-model="form.class_name"
                        type="text"
                        required
                        class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                        placeholder="例如：计工本2303"
                      />
                    </div>

                    <!-- Grade -->
                    <div>
                      <label for="grade" class="block text-sm font-medium leading-6 text-gray-900">
                        年级 <span class="text-red-500">*</span>
                      </label>
                      <input
                        id="grade"
                        v-model="form.grade"
                        type="text"
                        required
                        class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                        placeholder="例如：2023"
                      />
                    </div>

                    <!-- Role -->
                    <div>
                      <label for="role" class="block text-sm font-medium leading-6 text-gray-900">
                        角色 <span class="text-red-500">*</span>
                      </label>
                      <select
                        id="role"
                        v-model="form.role"
                        required
                        class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                      >
                        <option value="user">用户</option>
                        <option value="admin">管理员</option>
                      </select>
                    </div>

                    <!-- Password -->
                    <div>
                      <label for="password" class="block text-sm font-medium leading-6 text-gray-900">
                        密码 <span v-if="!isEditMode" class="text-red-500">*</span>
                      </label>
                      <input
                        id="password"
                        v-model="form.password"
                        type="password"
                        :required="!isEditMode"
                        class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                        :placeholder="isEditMode ? '留空则不修改密码' : '请输入密码'"
                      />
                    </div>
                  </div>
                </div>

                <!-- Error message -->
                <div v-if="error" class="mt-4 rounded-md bg-red-50 p-4">
                  <div class="flex">
                    <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
                    <div class="ml-3">
                      <h3 class="text-sm font-medium text-red-800">
                        {{ error }}
                      </h3>
                    </div>
                  </div>
                </div>

                <!-- Actions -->
                <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                  <button
                    type="submit"
                    :disabled="isLoading"
                    class="inline-flex w-full justify-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600 disabled:opacity-50 disabled:cursor-not-allowed sm:col-start-2"
                  >
                    <span v-if="isLoading" class="mr-2">
                      <div class="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                    </span>
                    {{ isLoading ? '保存中...' : '保存' }}
                  </button>
                  <button
                    type="button"
                    @click="$emit('close')"
                    class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0"
                  >
                    取消
                  </button>
                </div>
              </form>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue';
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline';
import type { User } from '@/types';

interface Props {
  isOpen: boolean;
  user?: User | null;
}

const props = withDefaults(defineProps<Props>(), {
  user: null,
});

const emit = defineEmits<{
  close: [];
  save: [userData: any];
}>();

const isLoading = ref(false);
const error = ref<string | null>(null);

const form = ref({
  student_id: '',
  full_name: '',
  class_name: '',
  grade: '',
  role: 'user' as 'user' | 'admin',
  password: '',
});

const isEditMode = computed(() => props.user !== null);

// Watch for user changes to populate form
watch(() => props.user, (newUser) => {
  if (newUser) {
    form.value = {
      student_id: newUser.student_id,
      full_name: newUser.full_name,
      class_name: newUser.class_name,
      grade: newUser.grade,
      role: newUser.role as 'user' | 'admin',
      password: '',
    };
  } else {
    // Reset form for new user
    form.value = {
      student_id: '',
      full_name: '',
      class_name: '',
      grade: '',
      role: 'user',
      password: '',
    };
  }
  error.value = null;
}, { immediate: true });

async function handleSubmit() {
  error.value = null;
  
  // Validation
  if (!form.value.student_id.trim()) {
    error.value = '请输入学号';
    return;
  }
  
  if (!form.value.full_name.trim()) {
    error.value = '请输入姓名';
    return;
  }
  
  if (!form.value.class_name.trim()) {
    error.value = '请输入班级';
    return;
  }
  
  if (!form.value.grade.trim()) {
    error.value = '请输入年级';
    return;
  }
  
  if (!isEditMode.value && !form.value.password.trim()) {
    error.value = '请输入密码';
    return;
  }
  
  isLoading.value = true;
  
  try {
    const userData: any = {
      student_id: form.value.student_id.trim(),
      full_name: form.value.full_name.trim(),
      class_name: form.value.class_name.trim(),
      grade: form.value.grade.trim(),
      role: form.value.role,
    };
    
    // Only include password if it's provided
    if (form.value.password.trim()) {
      userData.password = form.value.password.trim();
    }
    
    emit('save', userData);
  } catch (err: any) {
    error.value = err.message || '保存失败，请重试';
  } finally {
    isLoading.value = false;
  }
}
</script>
