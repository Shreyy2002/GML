'use client';

import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { api } from '@/lib/api';
import { storage } from '@/lib/storage';

const schema = z.object({
  username: z.string().min(1),
  password: z.string().min(8),
});

type LoginForm = z.infer<typeof schema>;

export default function LoginPage() {
  const router = useRouter();
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginForm>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: LoginForm) => {
    const res = await api.post('/auth/login/', data);
    storage.setToken(res.data.access);
    storage.setUser(res.data.user);
    router.push('/dashboard');
  };

  return (
    <main className="min-h-screen grid place-items-center bg-gradient-to-br from-teal-100 via-white to-orange-100 p-4">
      <form onSubmit={handleSubmit(onSubmit)} className="w-full max-w-md card space-y-4 animate-rise">
        <h1 className="text-2xl font-semibold">Sign in</h1>
        <input {...register('username')} placeholder="Username" className="w-full rounded-lg border p-2" />
        {errors.username && <p className="text-sm text-red-600">Username is required.</p>}
        <input {...register('password')} type="password" placeholder="Password" className="w-full rounded-lg border p-2" />
        {errors.password && <p className="text-sm text-red-600">Password must be at least 8 chars.</p>}
        <button disabled={isSubmitting} className="w-full rounded-lg bg-accent text-white py-2">{isSubmitting ? 'Signing in...' : 'Login'}</button>
      </form>
    </main>
  );
}
