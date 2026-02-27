'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { storage } from '@/lib/storage';
import { User } from '@/types';

export function useAuth(requiredRoles?: User['role'][]) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const token = storage.getToken();
    const currentUser = storage.getUser();
    if (!token || !currentUser) {
      router.replace('/login');
      return;
    }
    if (requiredRoles && !requiredRoles.includes(currentUser.role)) {
      router.replace('/dashboard');
      return;
    }
    setUser(currentUser);
    setReady(true);
  }, [requiredRoles, router]);

  return { user, ready };
}
