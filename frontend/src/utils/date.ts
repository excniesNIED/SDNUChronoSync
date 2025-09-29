/**
 * Date utility functions for the schedule management app
 */

export function formatDate(date: Date | string): string {
  const d = new Date(date);
  if (isNaN(d.getTime())) {
    return '';
  }
  return d.toISOString().split('T')[0];
}

export function formatDateChinese(date: Date | string): string {
  const d = new Date(date);
  if (isNaN(d.getTime())) {
    return '无效日期';
  }
  return d.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).replace(/\//g, '-'); // 将 / 替换为 -，格式为 YYYY-MM-DD
}

export function formatDateTime(date: Date | string): string {
  const d = new Date(date);
  if (isNaN(d.getTime())) {
    return '';
  }
  return d.toISOString().slice(0, 16);
}

export function formatDisplayDate(date: Date | string): string {
  const d = new Date(date);
  if (isNaN(d.getTime())) {
    return '无效日期';
  }
  return d.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

export function formatDisplayDateShort(date: Date | string): string {
  const d = new Date(date);
  if (isNaN(d.getTime())) {
    return '无效日期';
  }
  return d.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
}

export function formatDisplayTime(date: Date | string): string {
  const d = new Date(date);
  if (isNaN(d.getTime())) {
    return '无效时间';
  }
  return d.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatDisplayDateTime(date: Date | string): string {
  const d = new Date(date);
  if (isNaN(d.getTime())) {
    return '无效日期时间';
  }
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatDisplayDateTimeShort(date: Date | string): string {
  const d = new Date(date);
  if (isNaN(d.getTime())) {
    return '无效日期时间';
  }
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function getWeekStart(date: Date): Date {
  const d = new Date(date);
  const day = d.getDay();
  // 将星期一设为一周的开始：星期日(0)往前移6天，其他往前移(day-1)天
  const diff = d.getDate() - (day === 0 ? 6 : day - 1);
  return new Date(d.setDate(diff));
}

export function getWeekEnd(date: Date): Date {
  const weekStart = getWeekStart(date);
  const weekEnd = new Date(weekStart);
  weekEnd.setDate(weekStart.getDate() + 6);
  return weekEnd;
}

export function getMonthStart(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), 1);
}

export function getMonthEnd(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth() + 1, 0);
}

export function addDays(date: Date, days: number): Date {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

export function addWeeks(date: Date, weeks: number): Date {
  return addDays(date, weeks * 7);
}

export function addMonths(date: Date, months: number): Date {
  const result = new Date(date);
  result.setMonth(result.getMonth() + months);
  return result;
}

export function isSameDay(date1: Date, date2: Date): boolean {
  return (
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate()
  );
}

export function isToday(date: Date): boolean {
  return isSameDay(date, new Date());
}

export function getWeekDays(startDate: Date): Date[] {
  const days: Date[] = [];
  for (let i = 0; i < 7; i++) {
    days.push(addDays(startDate, i));
  }
  return days;
}

export function getCalendarDays(date: Date): Date[] {
  const monthStart = getMonthStart(date);
  const monthEnd = getMonthEnd(date);
  const calendarStart = getWeekStart(monthStart);
  const calendarEnd = getWeekEnd(monthEnd);

  const days: Date[] = [];
  let currentDate = new Date(calendarStart);

  while (currentDate <= calendarEnd) {
    days.push(new Date(currentDate));
    currentDate = addDays(currentDate, 1);
  }

  return days;
}
