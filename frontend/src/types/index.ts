// API Response Types
export interface User {
  id: number;
  student_id: string;
  full_name: string;
  class_name: string;
  grade: string;
  role: 'user' | 'admin';
  avatar_url?: string;
  created_at: string;
  updated_at?: string;
}

export interface Schedule {
  id: number;
  name: string;
  owner_id: number;
  status: '进行' | '结束' | '隐藏';
  start_date: string;  // Date in YYYY-MM-DD format
  total_weeks: number;
  class_times: { [key: string]: { start: string; end: string } };
  created_at: string;
  updated_at: string;
}

export interface Event {
  id: number;
  schedule_id: number;
  title: string;
  description?: string;
  location?: string;
  start_time: string;
  end_time: string;
  created_at: string;
  updated_at: string;
  owner?: User;
  schedule?: Schedule;      // 课表信息
  // New fields for detailed course information
  instructor?: string;      // 教师
  weeks_display?: string;   // 周数 (例: "1-16周")
  day_of_week?: number;     // 星期几 (1-7)
  period?: string;          // 节次 (例: "3-4节")
  weeks_input?: string;     // 原始输入的周数，如 "1,4-6"
  // Schedule adjustment fields
  is_override?: boolean;    // 是否为调休覆盖事件
  is_active?: boolean;      // 是否激活（用于逻辑删除）
  adjustment_id?: number;   // 关联调整操作ID
}

export interface LoginRequest {
  student_id: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  student_id: string;
  password: string;
  full_name: string;
  class_name: string;
  grade: string;
}

export interface ImportSessionResponse {
  session_id: string;
  csrftoken: string;
  captcha_image: string;
}

export interface ImportRequest {
  session_id: string;
  username: string;
  password: string;
  captcha: string;
  schedule_id?: number;
  action: string;
  schedule_name?: string;
  start_date?: string;
}

export interface ImportResponse {
  success: boolean;
  message: string;
  imported_count?: number;
  user_info?: any;
}

export interface CreateUserRequest {
  student_id: string;
  password: string;
  full_name: string;
  class_name: string;
  grade: string;
  role?: 'user' | 'admin';
}

export interface UpdateUserRequest {
  student_id?: string;
  full_name?: string;
  class_name?: string;
  grade?: string;
  role?: 'user' | 'admin';
  password?: string;
}

export interface ScheduleResponse extends Schedule {}

export interface ScheduleCreate {
  name: string;
  status?: '进行' | '结束' | '隐藏';
  start_date: string;
  total_weeks?: number;
  class_times?: { [key: string]: { start: string; end: string } };
}

export interface ScheduleUpdate {
  name?: string;
  status?: '进行' | '结束' | '隐藏';
  start_date?: string;
  total_weeks?: number;
  class_times?: { [key: string]: { start: string; end: string } };
}

export interface CreateEventRequest {
  title: string;
  description?: string;
  location?: string;
  start_time: string;
  end_time: string;
  instructor?: string;
  weeks_display?: string;
  day_of_week?: number;
  period?: string;
  weeks_input?: string;
}

export interface UpdateEventRequest {
  title?: string;
  description?: string;
  location?: string;
  start_time?: string;
  end_time?: string;
  instructor?: string;
  weeks_display?: string;
  day_of_week?: number;
  period?: string;
  weeks_input?: string;
}

export interface ScheduleFilter {
  start_date: string;
  end_date: string;
  user_ids?: string;
  class_name?: string;
  grade?: string;
  full_name_contains?: string;
  event_title_contains?: string;
}

// UI State Types
export interface FilterState {
  dateRange: {
    start: string;
    end: string;
  };
  selectedUserIds: number[];
  className: string;
  grade: string;
  nameKeyword: string;
  eventKeyword: string;
}

export interface CalendarViewMode {
  type: 'week' | 'month';
  date: Date;
}

// Component Props Types
export interface EventModalProps {
  isOpen: boolean;
  event?: Event | null;
  isAdmin?: boolean;
  users?: User[];
  onClose: () => void;
  onSave: (event: CreateEventRequest | UpdateEventRequest) => void;
  onDelete?: (eventId: number) => void;
}

export interface CalendarEvent extends Event {
  color: string;
  textColor: string;
}

// Schedule Adjustment Types
export interface ScheduleAdjustment {
  id: number;
  schedule_id: number;
  adjustment_type: 'HOLIDAY' | 'SWAP';
  original_date: string;
  target_date?: string;
  created_at: string;
}

export interface HolidayAdjustmentRequest {
  adjustment_type: 'HOLIDAY';
  holiday_date: string;
}

export interface SwapAdjustmentRequest {
  adjustment_type: 'SWAP';
  source_date: string;
  target_date: string;
}

export interface AdjustmentOperationResponse {
  success: boolean;
  message: string;
  adjustment_id?: number;
  affected_events: number;
}

// Team Types
export interface Team {
  id: number;
  name: string;
  team_code: string;
  creator_id: number;
  created_at: string;
  updated_at: string;
  creator?: User;
  members?: User[];
}

export interface TeamCreate {
  name: string;
}

export interface TeamUpdate {
  name?: string;
}

export interface TeamJoinRequest {
  team_code: string;
}

export interface TeamMemberAdd {
  student_id: string;
}

// Error Types
export interface ApiError {
  detail: string;
  status_code?: number;
}
