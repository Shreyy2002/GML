'use client';

import { ReactNode } from 'react';
import { useAuth } from '@/hooks/useAuth';
import Sidebar from './Sidebar';
import Skeleton from './Skeleton';

export default function AppShell({ children, roles }: { children: ReactNode; roles?: ('TEAM_MEMBER' | 'EVALUATOR' | 'ADMIN')[] }) {
  const { user, ready } = useAuth(roles);

  if (!ready || !user) {
    return (
      <main className="p-10 space-y-4">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-40 w-full" />
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-surface p-4 md:p-6">
      <div className="mx-auto max-w-7xl grid grid-cols-1 md:grid-cols-[256px_1fr] gap-4 animate-rise">
        <Sidebar user={user} />
        <section className="rounded-2xl bg-card p-4 md:p-6 shadow-sm">{children}</section>
      </div>
    </main>
  );
}
