import { User } from '@/types';

const TOKEN_KEY = 'gms_access_token';
const USER_KEY = 'gms_user';

export const storage = {
  getToken: (): string | null => (typeof window === 'undefined' ? null : localStorage.getItem(TOKEN_KEY)),
  setToken: (token: string) => localStorage.setItem(TOKEN_KEY, token),
  clearToken: () => localStorage.removeItem(TOKEN_KEY),
  getUser: (): User | null => {
    if (typeof window === 'undefined') return null;
    const raw = localStorage.getItem(USER_KEY);
    return raw ? (JSON.parse(raw) as User) : null;
  },
  setUser: (user: User) => localStorage.setItem(USER_KEY, JSON.stringify(user)),
  clearUser: () => localStorage.removeItem(USER_KEY),
};
