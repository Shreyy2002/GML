'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { User } from '@/types';

export default function Sidebar({ user }: { user: User }) {
  const pathname = usePathname();
  const links = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/goals', label: 'Goals' },
    { href: '/reports', label: 'Reports' },
  ];
  if (user.role === 'ADMIN') {
    links.push({ href: '/admin/teams', label: 'Teams' });
  }

  return (
    <aside className="w-full md:w-64 rounded-2xl bg-ink text-white p-4">
      <h1 className="text-xl font-semibold tracking-wide">GMS</h1>
      <p className="text-sm text-slate-300 mt-1">{user.username}</p>
      <nav className="mt-6 space-y-2">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={`block rounded-lg px-3 py-2 transition ${pathname === link.href ? 'bg-accent text-white' : 'hover:bg-slate-800'}`}
          >
            {link.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
