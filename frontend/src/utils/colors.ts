/**
 * Color utility functions for user event visualization
 */

// Material Design 3 color palette for user events
const USER_COLORS = [
  { bg: '#E3F2FD', border: '#2196F3', text: '#0D47A1' }, // Blue
  { bg: '#F3E5F5', border: '#9C27B0', text: '#4A148C' }, // Purple
  { bg: '#E8F5E8', border: '#4CAF50', text: '#1B5E20' }, // Green
  { bg: '#FFF3E0', border: '#FF9800', text: '#E65100' }, // Orange
  { bg: '#FCE4EC', border: '#E91E63', text: '#880E4F' }, // Pink
  { bg: '#E0F2F1', border: '#009688', text: '#004D40' }, // Teal
  { bg: '#F1F8E9', border: '#8BC34A', text: '#33691E' }, // Light Green
  { bg: '#FFF8E1', border: '#FFC107', text: '#FF6F00' }, // Amber
  { bg: '#EFEBE9', border: '#795548', text: '#3E2723' }, // Brown
  { bg: '#FAFAFA', border: '#607D8B', text: '#263238' }, // Blue Grey
  { bg: '#E8EAF6', border: '#3F51B5', text: '#1A237E' }, // Indigo
  { bg: '#F9FBE7', border: '#CDDC39', text: '#827717' }, // Lime
];

// Cache for consistent user color assignment
const userColorCache = new Map<number, typeof USER_COLORS[0]>();

/**
 * Get a consistent color for a user based on their ID
 */
export function getUserColor(userId: number | undefined | null): typeof USER_COLORS[0] {
  // 处理无效的 userId，使用默认值
  const validUserId = (typeof userId === 'number' && !isNaN(userId)) ? userId : 0;
  
  if (userColorCache.has(validUserId)) {
    return userColorCache.get(validUserId)!;
  }

  const colorIndex = validUserId % USER_COLORS.length;
  const color = USER_COLORS[colorIndex];
  userColorCache.set(validUserId, color);
  
  return color;
}

/**
 * Generate CSS classes for user events
 */
export function getUserEventClasses(userId: number | undefined | null): {
  background: string;
  border: string;
  text: string;
} {
  const color = getUserColor(userId);
  return {
    background: color.bg,
    border: color.border,
    text: color.text,
  };
}

/**
 * Get contrasting text color for a background color
 */
export function getContrastColor(backgroundColor: string): string {
  // Simple contrast calculation - in a real app you might want a more sophisticated algorithm
  const hex = backgroundColor.replace('#', '');
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  
  // Calculate luminance
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  
  return luminance > 0.5 ? '#000000' : '#FFFFFF';
}

/**
 * Generate a consistent color for an event based on owner name
 */
export function generateEventColor(ownerName: string): string {
  if (!ownerName) return USER_COLORS[0].border;
  
  // Simple hash function to generate consistent colors based on string
  let hash = 0;
  for (let i = 0; i < ownerName.length; i++) {
    const char = ownerName.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  
  const colorIndex = Math.abs(hash) % USER_COLORS.length;
  return USER_COLORS[colorIndex].border;
}

/**
 * Clear the user color cache (useful for testing or when users change)
 */
export function clearUserColorCache(): void {
  userColorCache.clear();
}
