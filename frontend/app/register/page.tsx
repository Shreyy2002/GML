'use client';

import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { api } from '@/lib/api';

const schema = z.object({
  username: z.string().min(3),
  email: z.string().email(),
  password: z.string().min(8),
  role: z.enum(['TEAM_MEMBER', 'EVALUATOR', 'ADMIN']),
});

type RegisterForm = z.infer<typeof schema>;

export default function RegisterPage() {
  const router = useRouter();
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<RegisterForm>({
    resolver: zodResolver(schema),
    defaultValues: { role: 'TEAM_MEMBER' },
  });

  const onSubmit = async (data: RegisterForm) => {
    await api.post('/auth/register/', data);
    router.push('/login');
  };

  return (
    <main className="min-h-screen grid place-items-center bg-gradient-to-br from-orange-100 via-white to-teal-100 p-4">
      <form onSubmit={handleSubmit(onSubmit)} className="w-full max-w-md card space-y-4 animate-rise">
        <h1 className="text-2xl font-semibold">Create account</h1>
        <input {...register('username')} placeholder="Username" className="w-full rounded-lg border p-2" />
        <input {...register('email')} placeholder="Email" className="w-full rounded-lg border p-2" />
        <input {...register('password')} type="password" placeholder="Password" className="w-full rounded-lg border p-2" />
        <select {...register('role')} className="w-full rounded-lg border p-2">
          <option value="TEAM_MEMBER">Team Member</option>
          <option value="EVALUATOR">Evaluator / Manager</option>
          <option value="ADMIN">Leadership / Admin</option>
        </select>
        {(errors.username || errors.email || errors.password) && <p className="text-sm text-red-600">Please provide valid values.</p>}
        <button disabled={isSubmitting} className="w-full rounded-lg bg-accent text-white py-2">Register</button>
      </form>
    </main>
  );
}
