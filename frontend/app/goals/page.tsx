'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

import AppShell from '@/components/AppShell';
import Skeleton from '@/components/Skeleton';
import { api } from '@/lib/api';
import { Goal } from '@/types';

const goalSchema = z.object({
  title: z.string().min(3),
  description: z.string().min(10),
  level: z.enum(['COMPANY', 'TEAM', 'INDIVIDUAL']),
  due_date: z.string(),
  weightage: z.string(),
  category: z.string().min(2),
});

type GoalForm = z.infer<typeof goalSchema>;

export default function GoalsPage() {
  const [goals, setGoals] = useState<Goal[] | null>(null);
  const { register, handleSubmit, reset, formState: { isSubmitting } } = useForm<GoalForm>({
    resolver: zodResolver(goalSchema),
    defaultValues: { level: 'INDIVIDUAL' },
  });

  const load = async () => {
    const res = await api.get('/goals/');
    setGoals(res.data);
  };

  useEffect(() => {
    load();
  }, []);

  const onCreate = async (payload: GoalForm) => {
    const optimistic: Goal = {
      id: Date.now(),
      ...payload,
      status: 'DRAFT',
      owner: 0,
      evaluator: null,
      team: null,
      parent_goal: null,
      completion_percentage: 0,
      final_score: null,
      at_risk: false,
      is_locked: false,
    };
    setGoals((prev) => (prev ? [optimistic, ...prev] : [optimistic]));
    await api.post('/goals/', payload);
    reset();
    await load();
  };

  const transition = async (id: number, action: 'submit' | 'complete') => {
    await api.post(`/goals/${id}/${action}/`, action === 'complete' ? { completion_percentage: 100 } : {});
    await load();
  };

  return (
    <AppShell>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <form onSubmit={handleSubmit(onCreate)} className="card space-y-2 lg:col-span-1">
          <h2 className="font-semibold">Create Goal</h2>
          <input {...register('title')} className="w-full border rounded p-2" placeholder="Title" />
          <textarea {...register('description')} className="w-full border rounded p-2" placeholder="Description" />
          <select {...register('level')} className="w-full border rounded p-2">
            <option value="INDIVIDUAL">Individual</option>
            <option value="TEAM">Team</option>
            <option value="COMPANY">Company</option>
          </select>
          <input {...register('due_date')} type="date" className="w-full border rounded p-2" />
          <input {...register('weightage')} className="w-full border rounded p-2" placeholder="Weightage %" />
          <input {...register('category')} className="w-full border rounded p-2" placeholder="Category" />
          <button disabled={isSubmitting} className="w-full rounded bg-accent text-white py-2">Save Goal</button>
        </form>
        <div className="lg:col-span-2 card">
          <h2 className="font-semibold mb-3">Goals</h2>
          {!goals ? (
            <Skeleton className="h-56 w-full" />
          ) : (
            <div className="space-y-3">
              {goals.map((goal) => (
                <article key={goal.id} className="border rounded-lg p-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <Link href={`/goals/${goal.id}`} className="font-medium hover:underline">{goal.title}</Link>
                    <span className="badge bg-slate-100">{goal.status}</span>
                  </div>
                  <div className="mt-2 h-2 w-full bg-slate-100 rounded-full">
                    <div className="h-2 rounded-full bg-accent transition-all duration-500" style={{ width: `${goal.completion_percentage}%` }} />
                  </div>
                  <div className="mt-3 flex gap-2">
                    {goal.status === 'DRAFT' || goal.status === 'REJECTED' ? (
                      <button onClick={() => transition(goal.id, 'submit')} className="rounded bg-ink text-white px-3 py-1 text-sm">Submit</button>
                    ) : null}
                    {goal.status === 'ACTIVE' ? (
                      <button onClick={() => transition(goal.id, 'complete')} className="rounded bg-accent2 text-white px-3 py-1 text-sm">Mark Complete</button>
                    ) : null}
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
