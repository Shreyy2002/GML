'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';

import AppShell from '@/components/AppShell';
import { api } from '@/lib/api';
import { Goal } from '@/types';

export default function GoalDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [goal, setGoal] = useState<Goal | null>(null);
  const memberForm = useForm({ defaultValues: { self_reflection: '', delivered: '', improvement: '' } });
  const evaluatorForm = useForm({
    defaultValues: { quality: 3, ownership: 3, communication: 3, timeliness: 3, initiative: 3, comment: '', final_rating: 'MEETS' },
  });

  const load = async () => {
    const res = await api.get(`/goals/${params.id}/`);
    setGoal(res.data);
  };

  useEffect(() => {
    load();
  }, [params.id]);

  if (!goal) {
    return <AppShell><p>Loading...</p></AppShell>;
  }

  return (
    <AppShell>
      <div className="space-y-4">
        <button onClick={() => router.push('/goals')} className="text-sm underline">Back</button>
        <article className="card">
          <h2 className="text-xl font-semibold">{goal.title}</h2>
          <p className="text-slate-600 mt-1">{goal.description}</p>
          <p className="text-sm mt-3">Status: <span className="badge bg-slate-100">{goal.status}</span></p>
        </article>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <form onSubmit={memberForm.handleSubmit(async (values) => { await api.post(`/goals/${goal.id}/member-feedback/`, values); await load(); })} className="card space-y-2">
            <h3 className="font-semibold">Member Feedback</h3>
            <textarea {...memberForm.register('self_reflection')} className="w-full border rounded p-2" placeholder="Self reflection" />
            <textarea {...memberForm.register('delivered')} className="w-full border rounded p-2" placeholder="What delivered" />
            <textarea {...memberForm.register('improvement')} className="w-full border rounded p-2" placeholder="What to improve" />
            <button className="rounded bg-ink text-white px-3 py-2">Submit Member Feedback</button>
          </form>

          <form onSubmit={evaluatorForm.handleSubmit(async (values) => { await api.post(`/goals/${goal.id}/evaluator-feedback/`, values); await load(); })} className="card space-y-2">
            <h3 className="font-semibold">Evaluator Feedback</h3>
            {['quality', 'ownership', 'communication', 'timeliness', 'initiative'].map((field) => (
              <input key={field} type="number" min={1} max={5} {...evaluatorForm.register(field as never, { valueAsNumber: true })} className="w-full border rounded p-2" placeholder={field} />
            ))}
            <textarea {...evaluatorForm.register('comment')} className="w-full border rounded p-2" placeholder="Comment" />
            <select {...evaluatorForm.register('final_rating')} className="w-full border rounded p-2">
              <option value="BELOW">Below</option>
              <option value="MEETS">Meets</option>
              <option value="ABOVE">Above</option>
            </select>
            <button className="rounded bg-accent text-white px-3 py-2">Submit Evaluator Feedback</button>
          </form>
        </div>

        <div className="card">
          <button onClick={async () => { await api.post(`/goals/${goal.id}/score/`); await load(); }} disabled={goal.status !== 'COMPLETED'} className="rounded bg-accent2 text-white px-4 py-2 disabled:opacity-50">Score Goal</button>
        </div>
      </div>
    </AppShell>
  );
}
