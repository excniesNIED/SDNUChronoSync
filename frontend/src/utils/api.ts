import axios from 'axios';
import type {
  User,
  Event,
  LoginRequest,
  TokenResponse,
  CreateUserRequest,
  UpdateUserRequest,
  CreateEventRequest,
  UpdateEventRequest,
  ScheduleFilter,
  ScheduleResponse,
  ScheduleCreate,
  ScheduleUpdate,
  RegisterRequest,
  ImportSessionResponse,
  ImportRequest,
  ImportResponse
} from '@/types';

const API_BASE_URL = 'http://localhost:8000';

class ApiClient {
  constructor() {
    // Configure axios defaults
    axios.defaults.baseURL = API_BASE_URL;
    axios.defaults.headers.common['Content-Type'] = 'application/json';

    // Request interceptor to add auth token
    axios.interceptors.request.use(
      (config) => {
        const token = this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle errors
    axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid, redirect to login
          this.removeToken();
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  private getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('access_token');
  }

  private setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  private removeToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
    }
  }

  // Auth endpoints
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    const response = await axios.post('/api/auth/token', credentials);
    this.setToken(response.data.access_token);
    return response.data;
  }

  async register(userData: {
    student_id: string;
    full_name: string;
    class_name: string;
    grade: string;
    password: string;
  }): Promise<User> {
    const response = await axios.post('/api/auth/register', userData);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await axios.get('/api/auth/users/me');
    return response.data;
  }

  logout(): void {
    this.removeToken();
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }

  // Personal schedule endpoints
  async getMyEvents(): Promise<Event[]> {
    const response = await axios.get('/api/schedule/');
    return response.data;
  }

  async createMyEvent(event: CreateEventRequest): Promise<Event> {
    const response = await axios.post('/api/schedule/', event);
    return response.data;
  }

  async updateMyEvent(eventId: number, event: UpdateEventRequest): Promise<Event> {
    const response = await axios.put(`/api/schedule/${eventId}`, event);
    return response.data;
  }

  async deleteMyEvent(eventId: number): Promise<void> {
    await axios.delete(`/api/schedule/${eventId}`);
  }

  async exportMySchedule(): Promise<Blob> {
    const response = await axios.get('/api/schedule/export/ics', {
      responseType: 'blob',
    });
    return response.data;
  }

  // Team endpoints
  async getAllUsers(): Promise<User[]> {
    const response = await axios.get('/api/team/users');
    return response.data;
  }

  async getUserSchedule(userId: number): Promise<Event[]> {
    const response = await axios.get(`/api/team/schedule/user/${userId}`);
    return response.data;
  }

  async getFilteredSchedule(filter: ScheduleFilter): Promise<Event[]> {
    const params = new URLSearchParams();
    params.append('start_date', filter.start_date);
    params.append('end_date', filter.end_date);
    
    if (filter.user_ids) params.append('user_ids', filter.user_ids);
    if (filter.class_name) params.append('class_name', filter.class_name);
    if (filter.grade) params.append('grade', filter.grade);
    if (filter.full_name_contains) params.append('full_name_contains', filter.full_name_contains);
    if (filter.event_title_contains) params.append('event_title_contains', filter.event_title_contains);

    const response = await axios.get(`/api/team/schedule/filtered?${params.toString()}`);
    return response.data;
  }

  // Admin endpoints
  async getAllUsersAdmin(): Promise<User[]> {
    const response = await axios.get('/api/admin/users');
    return response.data;
  }

  async createUser(user: CreateUserRequest): Promise<User> {
    const response = await axios.post('/api/admin/users', user);
    return response.data;
  }

  async updateUser(userId: number, user: UpdateUserRequest): Promise<User> {
    const response = await axios.put(`/api/admin/users/${userId}`, user);
    return response.data;
  }

  async deleteUser(userId: number): Promise<void> {
    await axios.delete(`/api/admin/users/${userId}`);
  }

  async createEventForUser(userId: number, event: CreateEventRequest): Promise<Event> {
    const response = await axios.post(`/api/admin/schedule/${userId}`, event);
    return response.data;
  }

  async updateAnyEvent(eventId: number, event: UpdateEventRequest): Promise<Event> {
    const response = await axios.put(`/api/admin/schedule/${eventId}`, event);
    return response.data;
  }

  async deleteAnyEvent(eventId: number): Promise<void> {
    await axios.delete(`/api/admin/schedule/${eventId}`);
  }

  // Import endpoints
  async getImportSession(): Promise<{
    session_id: string;
    csrftoken: string;
    captcha_image: string;
  }> {
    const response = await axios.get('/api/import/zfw/session');
    return response.data;
  }

  async importFromZFW(importData: { 
    session_id: string; 
    username: string; 
    password: string; 
    captcha: string; 
  }): Promise<{
    success: boolean;
    message: string;
    imported_count: number;
  }> {
    const response = await axios.post('/api/import/zfw', importData);
    return response.data;
  }

  async refreshCaptcha(sessionId: string): Promise<{
    session_id: string;
    csrftoken: string;
    captcha_image: string;
  }> {
    const response = await axios.get(`/api/import/zfw/refresh/${sessionId}`);
    return response.data;
  }

  async testLogin(importData: { 
    session_id: string; 
    username: string; 
    password: string; 
    captcha: string; 
  }): Promise<{
    success: boolean;
    message: string;
    details: string[];
    working_url?: string;
  }> {
    const response = await axios.post('/api/import/test-login', importData);
    return response.data;
  }

  async testImportConnection(): Promise<{
    status: string;
    message: string;
  }> {
    const response = await axios.get('/api/import/test');
    return response.data;
  }

  // Schedule management endpoints
  async getSchedules(): Promise<ScheduleResponse[]> {
    const response = await axios.get('/api/schedules/');
    return response.data;
  }

  async createSchedule(scheduleData: ScheduleCreate): Promise<ScheduleResponse> {
    const response = await axios.post('/api/schedules/', scheduleData);
    return response.data;
  }

  async getSchedule(scheduleId: number): Promise<ScheduleResponse> {
    const response = await axios.get(`/api/schedules/${scheduleId}`);
    return response.data;
  }

  async updateSchedule(scheduleId: number, scheduleData: ScheduleUpdate): Promise<ScheduleResponse> {
    const response = await axios.put(`/api/schedules/${scheduleId}`, scheduleData);
    return response.data;
  }

  async deleteSchedule(scheduleId: number): Promise<void> {
    await axios.delete(`/api/schedules/${scheduleId}`);
  }

  async getScheduleEvents(scheduleId: number): Promise<Event[]> {
    const response = await axios.get(`/api/schedules/${scheduleId}/events`);
    return response.data;
  }

  async createScheduleEvent(scheduleId: number, eventData: CreateEventRequest): Promise<Event> {
    const response = await axios.post(`/api/schedules/${scheduleId}/events`, eventData);
    return response.data;
  }

  async updateScheduleEvent(scheduleId: number, eventId: number, eventData: UpdateEventRequest): Promise<Event> {
    const response = await axios.put(`/api/schedules/${scheduleId}/events/${eventId}`, eventData);
    return response.data;
  }

  async deleteScheduleEvent(scheduleId: number, eventId: number): Promise<void> {
    await axios.delete(`/api/schedules/${scheduleId}/events/${eventId}`);
  }

  async exportScheduleToICS(scheduleId: number): Promise<Blob> {
    const response = await axios.get(`/api/schedules/${scheduleId}/export.ics`, {
      responseType: 'blob',
    });
    return response.data;
  }

  // Utility methods
  isAuthenticated(): boolean {
    return this.getToken() !== null;
  }
}

export const apiClient = new ApiClient();
