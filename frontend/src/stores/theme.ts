import { ref, watch } from 'vue';

export type Theme = 'light' | 'dark';

const THEME_STORAGE_KEY = 'app-theme';

// Get initial theme from localStorage or default to 'light'
const getInitialTheme = (): Theme => {
  if (typeof window === 'undefined') return 'light';
  const stored = localStorage.getItem(THEME_STORAGE_KEY);
  return (stored === 'dark' ? 'dark' : 'light') as Theme;
};

const theme = ref<Theme>(getInitialTheme());

// Apply theme to document
const applyTheme = (newTheme: Theme) => {
  if (typeof window === 'undefined') return;
  
  if (newTheme === 'dark') {
    document.documentElement.classList.add('dark-mode');
  } else {
    document.documentElement.classList.remove('dark-mode');
  }
};

// Watch for theme changes and persist to localStorage
if (typeof window !== 'undefined') {
  watch(theme, (newTheme) => {
    localStorage.setItem(THEME_STORAGE_KEY, newTheme);
    applyTheme(newTheme);
  }, { immediate: true });
}

export const useThemeStore = () => {
  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light';
  };

  const setTheme = (newTheme: Theme) => {
    theme.value = newTheme;
  };

  const isDark = () => theme.value === 'dark';

  return {
    theme,
    toggleTheme,
    setTheme,
    isDark,
  };
};
