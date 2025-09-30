<template>
  <div class="space-y-8">
    <!-- Page Header -->
    <div class="text-center sm:text-left">
      <h1 class="text-3xl font-bold text-gray-900">我的团队</h1>
      <p class="mt-2 text-lg text-gray-600">创建团队、加入团队或管理现有团队</p>
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">我的团队</dt>
                <dd class="text-lg font-medium text-gray-900">{{ teams.length }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">创建的团队</dt>
                <dd class="text-lg font-medium text-gray-900">{{ createdTeams.length }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">总成员数</dt>
                <dd class="text-lg font-medium text-gray-900">{{ totalMembers }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Team Management Section -->
    <div class="bg-white shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-lg leading-6 font-medium text-gray-900 mb-6">团队管理</h3>
        
        <div class="grid gap-6 lg:grid-cols-2">
          <!-- Create Team -->
          <div class="space-y-4">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="flex items-center justify-center h-10 w-10 rounded-md bg-indigo-500">
                  <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                  </svg>
                </div>
              </div>
              <div class="ml-4">
                <h4 class="text-lg font-medium text-gray-900">创建新团队</h4>
                <p class="text-sm text-gray-500">创建一个新的团队并邀请成员加入</p>
              </div>
            </div>
            
            <form @submit.prevent="handleCreateTeam" class="space-y-4">
              <div>
                <label for="newTeamName" class="block text-sm font-medium text-gray-700">
                  团队名称
                </label>
                <div class="mt-1">
                  <input
                    id="newTeamName"
                    v-model="newTeamName"
                    type="text"
                    required
                    placeholder="请输入团队名称"
                    class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    :disabled="creating"
                  />
                </div>
              </div>
              
              <div class="flex justify-end">
                <button
                  type="submit"
                  :disabled="creating || !newTeamName.trim()"
                  class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg v-if="creating" class="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ creating ? '创建中...' : '创建团队' }}
                </button>
              </div>
            </form>
          </div>

          <!-- Join Team -->
          <div class="space-y-4">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="flex items-center justify-center h-10 w-10 rounded-md bg-green-500">
                  <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
                  </svg>
                </div>
              </div>
              <div class="ml-4">
                <h4 class="text-lg font-medium text-gray-900">加入团队</h4>
                <p class="text-sm text-gray-500">使用团队代码加入现有团队</p>
              </div>
            </div>
            
            <form @submit.prevent="handleJoinTeam" class="space-y-4">
              <div>
                <label for="teamCode" class="block text-sm font-medium text-gray-700">
                  团队代码
                </label>
                <div class="mt-1">
                  <input
                    id="teamCode"
                    v-model="teamCode"
                    type="text"
                    required
                    placeholder="请输入8位团队代码"
                    maxlength="8"
                    class="shadow-sm focus:ring-green-500 focus:border-green-500 block w-full sm:text-sm border-gray-300 rounded-md uppercase tracking-wider font-mono"
                    :disabled="joining"
                    @input="teamCode = teamCode.toUpperCase()"
                  />
                </div>
                <p class="mt-1 text-xs text-gray-500">团队代码由8位字母和数字组成</p>
              </div>
              
              <div class="flex justify-end">
                <button
                  type="submit"
                  :disabled="joining || !isValidTeamCode"
                  class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg v-if="joining" class="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ joining ? '加入中...' : '加入团队' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Success Messages -->
    <div v-if="successMessage" class="rounded-md bg-green-50 p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm font-medium text-green-800">{{ successMessage }}</p>
        </div>
        <div class="ml-auto pl-3">
          <div class="-mx-1.5 -my-1.5">
            <button
              @click="successMessage = ''"
              type="button"
              class="inline-flex bg-green-50 rounded-md p-1.5 text-green-500 hover:bg-green-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-green-50 focus:ring-green-600"
            >
              <svg class="h-3 w-3" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Messages -->
    <div v-if="errorMessage" class="rounded-md bg-red-50 p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm font-medium text-red-800">{{ errorMessage }}</p>
        </div>
        <div class="ml-auto pl-3">
          <div class="-mx-1.5 -my-1.5">
            <button
              @click="errorMessage = ''"
              type="button"
              class="inline-flex bg-red-50 rounded-md p-1.5 text-red-500 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-red-50 focus:ring-red-600"
            >
              <svg class="h-3 w-3" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Teams List -->
    <div class="bg-white shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900">我的团队列表</h3>
          <button
            @click="refreshTeams"
            :disabled="loading"
            class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            <svg 
              class="w-4 h-4 mr-2" 
              :class="{ 'animate-spin': loading }" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            刷新
          </button>
        </div>

        <!-- Loading State -->
        <div v-if="loading && teams.length === 0" class="text-center py-12">
          <svg class="animate-spin h-8 w-8 text-indigo-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p class="mt-4 text-lg text-gray-600">正在加载您的团队...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="teams.length === 0" class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <h3 class="mt-2 text-sm font-semibold text-gray-900">还没有团队</h3>
          <p class="mt-1 text-sm text-gray-500">开始创建您的第一个团队或加入现有团队</p>
          <div class="mt-6 flex justify-center gap-3">
            <button
              @click="scrollToManagement"
              class="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
            >
              <svg class="-ml-0.5 mr-1.5 h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z" />
              </svg>
              创建团队
            </button>
          </div>
        </div>

        <!-- Teams Grid -->
        <div v-else class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <div 
            v-for="team in teams" 
            :key="team.id" 
            class="bg-gray-50 rounded-lg p-6 hover:shadow-md transition-shadow duration-200"
          >
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="h-10 w-10 bg-indigo-100 rounded-full flex items-center justify-center">
                    <span class="text-sm font-medium text-indigo-800">{{ team.name.charAt(0) }}</span>
                  </div>
                </div>
                <div class="ml-3">
                  <h4 class="text-lg font-medium text-gray-900">{{ team.name }}</h4>
                  <p class="text-sm text-gray-500">{{ team.members?.length || 0 }} 名成员</p>
                </div>
              </div>
              <div class="flex-shrink-0">
                <span 
                  :class="[
                    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                    isCreator(team) ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                  ]"
                >
                  {{ isCreator(team) ? '创建者' : '成员' }}
                </span>
              </div>
            </div>

            <div class="mb-4 p-3 bg-white rounded-lg">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-xs text-gray-500 mb-1">团队代码</p>
                  <p class="text-sm font-mono font-semibold text-gray-900 tracking-wider">
                    {{ team.team_code }}
                  </p>
                </div>
                <button
                  @click="copyTeamCode(team.team_code)"
                  class="text-gray-400 hover:text-gray-600 focus:outline-none"
                  title="复制团队代码"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Button Layout: 2 rows, 1 column -->
            <div class="space-y-2">
              <!-- First Row: 查看课表 -->
              <button
                @click="viewTeam(team.id)"
                class="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3a4 4 0 118 0v4m-4 1v0a8 8 0 00-7.864 9.746l.349 2.083A2 2 0 006.464 17h11.072a2 2 0 001.979-1.669l.349-2.083A8 8 0 0012 8v0z" />
                </svg>
                查看课表
              </button>
              
              <!-- Second Row: 根据用户角色显示不同按钮 -->
              <!-- 创建者：管理团队 -->
              <button
                v-if="isCreator(team)"
                @click="openCreatorManagement"
                class="w-full inline-flex items-center justify-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                管理团队
              </button>
              
              <!-- 非创建者：退出团队 -->
              <button
                v-else
                @click="openLeaveModal(team)"
                class="w-full inline-flex items-center justify-center px-4 py-2 border border-red-300 shadow-sm text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                退出团队
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Copy Success Toast -->
    <div
      v-if="showCopySuccess"
      class="fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-md shadow-lg z-50"
    >
      团队代码已复制到剪贴板
    </div>

    <!-- Team Editor Modal -->
    <TeamEditorModal
      v-if="showManageModal && selectedTeam"
      :team="selectedTeam"
      :user="user"
      @close="closeManageModal"
      @updated="handleTeamUpdated"
    />

    <!-- Creator Team Management Modal -->
    <CreatorTeamManagement
      v-if="showCreatorManagement"
      :user="user"
      @close="closeCreatorManagement"
      @updated="handleCreatorManagementUpdated"
    />

    <!-- Leave Team Modal -->
    <LeaveTeamModal
      v-if="showLeaveModal && selectedTeam"
      :team="selectedTeam"
      @close="closeLeaveModal"
      @left="handleTeamLeft"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useTeamStore } from '@/stores/team';
import { useAuthStore } from '@/stores/auth';
import TeamEditorModal from './TeamEditorModal.vue';
import CreatorTeamManagement from './CreatorTeamManagement.vue';
import LeaveTeamModal from './LeaveTeamModal.vue';
import type { Team } from '@/types';

// Stores
const teamStore = useTeamStore();
const authStore = useAuthStore();

// Reactive state
const newTeamName = ref('');
const teamCode = ref('');
const creating = ref(false);
const joining = ref(false);
// leavingTeamId 已移除，退出功能在模态框中处理
const showCopySuccess = ref(false);
const showManageModal = ref(false);
const showCreatorManagement = ref(false);
const showLeaveModal = ref(false);
const selectedTeam = ref<Team | null>(null);
const successMessage = ref('');
const errorMessage = ref('');

// Computed properties
const teams = computed(() => teamStore.teams);
const loading = computed(() => teamStore.loading);
const user = computed(() => authStore.user);

const createdTeams = computed(() => {
  return teams.value.filter(team => isCreator(team));
});

const totalMembers = computed(() => {
  return teams.value.reduce((total, team) => total + (team.members?.length || 0), 0);
});

const isValidTeamCode = computed(() => {
  return teamCode.value.length === 8 && /^[A-Z0-9]+$/.test(teamCode.value);
});

// Methods
const isCreator = (team: Team): boolean => {
  return user.value?.id === team.creator_id;
};

const canManage = (team: Team): boolean => {
  return user.value?.role === 'admin' || isCreator(team);
};

const refreshTeams = async () => {
  try {
    await teamStore.fetchMyTeams();
  } catch (error) {
    console.error('Failed to fetch teams:', error);
    showError('获取团队列表失败，请重试');
  }
};

const handleCreateTeam = async () => {
  try {
    creating.value = true;
    const team = await teamStore.createTeam({ name: newTeamName.value });
    newTeamName.value = '';
    showSuccess(`团队"${team.name}"创建成功！团队代码：${team.team_code}`);
    await refreshTeams();
  } catch (error: any) {
    console.error('Failed to create team:', error);
    showError(error.response?.data?.detail || '创建团队失败，请重试');
  } finally {
    creating.value = false;
  }
};

const handleJoinTeam = async () => {
  try {
    joining.value = true;
    const team = await teamStore.joinTeam({ team_code: teamCode.value });
    teamCode.value = '';
    showSuccess(`成功加入团队"${team.name}"！`);
    await refreshTeams();
  } catch (error: any) {
    console.error('Failed to join team:', error);
    if (error.response?.status === 404) {
      showError('团队代码不存在，请检查后重试');
    } else if (error.response?.status === 400) {
      showError('您已经是该团队的成员了');
    } else {
      showError(error.response?.data?.detail || '加入团队失败，请重试');
    }
  } finally {
    joining.value = false;
  }
};

const viewTeam = (teamId: number) => {
  window.location.href = `/dashboard/team-view?teamId=${teamId}`;
};

const copyTeamCode = async (code: string) => {
  try {
    await navigator.clipboard.writeText(code);
    showCopySuccess.value = true;
    setTimeout(() => {
      showCopySuccess.value = false;
    }, 2000);
  } catch (err) {
    console.error('Failed to copy team code:', err);
    showError('复制失败，请手动复制团队代码');
  }
};

const openManageModal = (team: Team) => {
  selectedTeam.value = team;
  showManageModal.value = true;
};

const closeManageModal = () => {
  showManageModal.value = false;
  selectedTeam.value = null;
};

const handleTeamUpdated = () => {
  refreshTeams();
  closeManageModal();
  showSuccess('团队信息更新成功！');
};

const openCreatorManagement = () => {
  showCreatorManagement.value = true;
};

const closeCreatorManagement = () => {
  showCreatorManagement.value = false;
};

const handleCreatorManagementUpdated = () => {
  refreshTeams();
  showSuccess('团队管理操作完成！');
};

const openLeaveModal = (team: Team) => {
  selectedTeam.value = team;
  showLeaveModal.value = true;
};

const closeLeaveModal = () => {
  showLeaveModal.value = false;
  selectedTeam.value = null;
};

const handleTeamLeft = async () => {
  await refreshTeams();
  closeLeaveModal();
  showSuccess('已退出团队');
};

const scrollToManagement = () => {
  document.querySelector('.bg-white.shadow.sm\\:rounded-lg')?.scrollIntoView({ 
    behavior: 'smooth' 
  });
};

const showSuccess = (message: string) => {
  successMessage.value = message;
  errorMessage.value = '';
  setTimeout(() => {
    successMessage.value = '';
  }, 5000);
};

const showError = (message: string) => {
  errorMessage.value = message;
  successMessage.value = '';
};

// Lifecycle
onMounted(async () => {
  try {
    // 确保认证状态已初始化
    await authStore.initialize();
    
    if (!authStore.isAuthenticated) {
      window.location.href = '/login';
      return;
    }
    
    await refreshTeams();
  } catch (error) {
    console.error('初始化失败:', error);
  }
});
</script>
