import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

const useThemeStore = create(
  persist(
    (set) => ({
      theme: 'dark', // 'dark' or 'light'
      
      toggleTheme: () => {
        set((state) => ({
          theme: state.theme === 'dark' ? 'light' : 'dark',
        }));
        // Apply theme to document
        const newTheme = useThemeStore.getState().theme === 'dark' ? 'dark' : 'light';
        document.documentElement.classList.toggle('dark', newTheme === 'dark');
      },
      
      setTheme: (theme) => {
        set({ theme });
        document.documentElement.classList.toggle('dark', theme === 'dark');
      },
    }),
    {
      name: 'theme-storage',
      storage: createJSONStorage(() => localStorage),
      onRehydrateStorage: () => (state) => {
        // Apply theme on rehydrate
        if (state?.theme) {
          document.documentElement.classList.toggle('dark', state.theme === 'dark');
        }
      },
    }
  )
);

// Initialize theme on load
if (typeof window !== 'undefined') {
  const storedTheme = localStorage.getItem('theme-storage');
  if (storedTheme) {
    try {
      const parsed = JSON.parse(storedTheme);
      if (parsed?.state?.theme) {
        document.documentElement.classList.toggle('dark', parsed.state.theme === 'dark');
      }
    } catch (e) {
      // Default to dark
      document.documentElement.classList.add('dark');
    }
  } else {
    // Default to dark
    document.documentElement.classList.add('dark');
  }
}

export default useThemeStore;
