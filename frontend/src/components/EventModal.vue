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
                      {{ isEditMode ? '编辑日程' : '创建日程' }}
                    </DialogTitle>
                  </div>

                  <div class="mt-6 space-y-4">
                    <!-- Title -->
                    <div>
                      <label for="title" class="block text-sm font-medium leading-6 text-gray-900">
                        标题 <span class="text-red-500">*</span>
                      </label>
                      <input
                        id="title"
                        v-model="form.title"
                        type="text"
                        required
                        class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                        placeholder="请输入日程标题"
                      />
                    </div>

                    <!-- Description -->
                    <div>
                      <label for="description" class="block text-sm font-medium leading-6 text-gray-900">
                        描述
                      </label>
                      <textarea
                        id="description"
                        v-model="form.description"
                        rows="3"
                        class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                        placeholder="请输入日程描述"
                      />
                    </div>

                    <!-- Location -->
                    <div>
                      <label for="location" class="block text-sm font-medium leading-6 text-gray-900">
                        地点
                      </label>
                      <input
                        id="location"
                        v-model="form.location"
                        type="text"
                        class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                        placeholder="请输入地点"
                      />
                    </div>

                    <!-- Instructor -->
                    <div>
                      <label for="instructor" class="block text-sm font-medium leading-6 text-gray-900">
                        教师
                      </label>
                      <input
                        id="instructor"
                        v-model="form.instructor"
                        type="text"
                        class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                        placeholder="请输入教师姓名"
                      />
                    </div>

                    <!-- Course Details -->
                    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                      <div>
                        <label for="weeks_display" class="block text-sm font-medium leading-6 text-gray-900">
                          周数
                        </label>
                        <input
                          id="weeks_display"
                          v-model="form.weeks_display"
                          type="text"
                          class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                          placeholder="例：1-16周"
                        />
                      </div>
                      <div>
                        <label for="period" class="block text-sm font-medium leading-6 text-gray-900">
                          节次
                        </label>
                        <input
                          id="period"
                          v-model="form.period"
                          type="text"
                          class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                          placeholder="例：1-2节"
                        />
                      </div>
                    </div>

                    <!-- Date and Time -->
                    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                      <div>
                        <label for="start_time" class="block text-sm font-medium leading-6 text-gray-900">
                          开始时间 <span class="text-red-500">*</span>
                        </label>
                        <input
                          id="start_time"
                          v-model="form.start_time"
                          type="datetime-local"
                          required
                          class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                        />
                      </div>
                      <div>
                        <label for="end_time" class="block text-sm font-medium leading-6 text-gray-900">
                          结束时间 <span class="text-red-500">*</span>
                        </label>
                        <input
                          id="end_time"
                          v-model="form.end_time"
                          type="datetime-local"
                          required
                          class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                        />
                      </div>
                    </div>

                    <!-- Owner selection (Admin only) -->
                    <div v-if="isAdmin && users && users.length > 0">
                      <label for="owner_id" class="block text-sm font-medium leading-6 text-gray-900">
                        所属用户 <span class="text-red-500">*</span>
                      </label>
                      <select
                        id="owner_id"
                        v-model="form.owner_id"
                        required
                        class="mt-1 block w-full rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                      >
                        <option value="">请选择用户</option>
                        <option
                          v-for="user in users"
                          :key="user.id"
                          :value="user.id"
                        >
                          {{ user.full_name }} ({{ user.student_id }}) - {{ user.class_name }}
                        </option>
                      </select>
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

                <!-- Delete button (for existing events) -->
                <div v-if="isEditMode && onDelete" class="mt-4 pt-4 border-t border-gray-200">
                  <button
                    type="button"
                    @click="handleDelete"
                    class="inline-flex w-full justify-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600"
                  >
                    删除日程
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
import { formatDateTime } from '@/utils/date';
import type { Event, User } from '@/types';

interface Props {
  isOpen: boolean;
  event?: Event | null;
  isAdmin?: boolean;
  users?: User[];
}

const props = withDefaults(defineProps<Props>(), {
  isAdmin: false,
  users: () => [],
});

const emit = defineEmits<{
  close: [];
  save: [eventData: any];
  delete?: [eventId: number];
}>();

const isLoading = ref(false);
const error = ref<string | null>(null);

const form = ref({
  title: '',
  description: '',
  location: '',
  start_time: '',
  end_time: '',
  owner_id: undefined as number | undefined,
  instructor: '',
  weeks_display: '',
  day_of_week: undefined as number | undefined,
  period: '',
});

const isEditMode = computed(() => props.event && props.event.id > 0);
const onDelete = computed(() => emit);

// Watch for event changes to populate form
watch(() => props.event, (newEvent) => {
  if (newEvent) {
    form.value = {
      title: newEvent.title || '',
      description: newEvent.description || '',
      location: newEvent.location || '',
      start_time: formatDateTime(newEvent.start_time),
      end_time: formatDateTime(newEvent.end_time),
      owner_id: newEvent.owner_id,
      instructor: newEvent.instructor || '',
      weeks_display: newEvent.weeks_display || '',
      day_of_week: newEvent.day_of_week,
      period: newEvent.period || '',
    };
  } else {
    // Reset form for new event
    const now = new Date();
    const oneHourLater = new Date(now.getTime() + 60 * 60 * 1000);
    
    form.value = {
      title: '',
      description: '',
      location: '',
      start_time: formatDateTime(now),
      end_time: formatDateTime(oneHourLater),
      owner_id: undefined,
      instructor: '',
      weeks_display: '',
      day_of_week: undefined,
      period: '',
    };
  }
  error.value = null;
}, { immediate: true });

async function handleSubmit() {
  error.value = null;
  
  // Validation
  if (!form.value.title.trim()) {
    error.value = '请输入日程标题';
    return;
  }
  
  if (!form.value.start_time || !form.value.end_time) {
    error.value = '请选择开始和结束时间';
    return;
  }
  
  const startTime = new Date(form.value.start_time);
  const endTime = new Date(form.value.end_time);
  
  if (startTime >= endTime) {
    error.value = '结束时间必须晚于开始时间';
    return;
  }

  if (isAdmin && !form.value.owner_id) {
    error.value = '请选择所属用户';
    return;
  }
  
  isLoading.value = true;
  
  try {
    const eventData = {
      title: form.value.title.trim(),
      description: form.value.description?.trim() || undefined,
      location: form.value.location?.trim() || undefined,
      start_time: new Date(form.value.start_time).toISOString(),
      end_time: new Date(form.value.end_time).toISOString(),
      owner_id: form.value.owner_id,
    };
    
    emit('save', eventData);
  } catch (err: any) {
    error.value = err.message || '保存失败，请重试';
  } finally {
    isLoading.value = false;
  }
}

function handleDelete() {
  if (props.event?.id && emit) {
    emit('delete', props.event.id);
  }
}
</script>
