'use client';

import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';

import AppShell from '@/components/AppShell';
import { api } from '@/lib/api';

type TeamForm = { name: string; description: string; evaluator: number | '' };

export default function AdminTeamsPage() {
  const [teams, setTeams] = useState<any[]>([]);
  const [evaluators, setEvaluators] = useState<any[]>([]);
  const form = useForm<TeamForm>({ defaultValues: { evaluator: '' } });

  const load = async () => {
    const [teamRes, userRes] = await Promise.all([
      api.get('/teams/'),
      api.get('/users/', { params: { role: 'EVALUATOR' } }),
    ]);
    setTeams(teamRes.data);
    setEvaluators(userRes.data);
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <AppShell roles={['ADMIN']}>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <form onSubmit={form.handleSubmit(async (v) => { await api.post('/teams/', v); form.reset(); await load(); })} className="card space-y-2">
          <h2 className="font-semibold">Create Team</h2>
          <input {...form.register('name')} className="w-full border rounded p-2" placeholder="Team name" />
          <textarea {...form.register('description')} className="w-full border rounded p-2" placeholder="Description" />
          <select {...form.register('evaluator', { valueAsNumber: true })} className="w-full border rounded p-2">
            <option value="">No evaluator</option>
            {evaluators.map((e) => <option key={e.id} value={e.id}>{e.username}</option>)}
          </select>
          <button className="rounded bg-accent text-white px-3 py-2">Create</button>
        </form>
        <div className="lg:col-span-2 card">
          <h2 className="font-semibold mb-3">Teams</h2>
          <div className="space-y-2">
            {teams.map((t) => (
              <article key={t.id} className="rounded border p-2">
                <h3 className="font-medium">{t.name}</h3>
                <p className="text-sm text-slate-600">Evaluator: {t.evaluator || 'Unassigned'}</p>
              </article>
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
