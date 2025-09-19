// API Response Types
export interface User {
  id: number;
  student_id: string;
  full_name: string;
  class_name: string;
  grade: string;
  role: 'user' | 'admin';
  created_at: string;
}

export interface Event {
  id: number;
  owner_id: number;
  title: string;
  description?: string;
  location?: string;
  start_time: string;
  end_time: string;
  created_at: string;
  updated_at: string;
  owner?: User;
}

export interface LoginRequest {
  student_id: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
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

export interface CreateEventRequest {
  title: string;
  description?: string;
  location?: string;
  start_time: string;
  end_time: string;
  owner_id?: number; // For admin use
}

export interface UpdateEventRequest {
  title?: string;
  description?: string;
  location?: string;
  start_time?: string;
  end_time?: string;
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

// Error Types
export interface ApiError {
  detail: string;
  status_code?: number;
}
