'use client';

import { useEffect, useMemo, useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import AppShell from '@/components/AppShell';
import Skeleton from '@/components/Skeleton';
import { api } from '@/lib/api';
import { DashboardResponse } from '@/types';

const COLORS = ['#0d9488', '#0284c7', '#f97316', '#ef4444', '#64748b'];

export default function DashboardPage() {
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [scope, setScope] = useState('individual');
  const [period, setPeriod] = useState('');

  useEffect(() => {
    api.get('/dashboard/', { params: { scope, month: period || undefined } }).then((res) => setData(res.data));
  }, [scope, period]);

  const chartData = useMemo(() => {
    if (!data) return [];
    return Object.entries(data.status_breakdown).map(([name, value]) => ({ name, value }));
  }, [data]);

  return (
    <AppShell>
      <div className="space-y-4">
        <div className="flex flex-wrap gap-3 items-end">
          <div>
            <label className="text-xs">Scope</label>
            <select className="block rounded border p-2" value={scope} onChange={(e) => setScope(e.target.value)}>
              <option value="individual">Individual</option>
              <option value="team">Team</option>
              <option value="company">Company</option>
            </select>
          </div>
          <div>
            <label className="text-xs">Month (YYYY-MM)</label>
            <input className="block rounded border p-2" value={period} onChange={(e) => setPeriod(e.target.value)} placeholder="2026-02" />
          </div>
        </div>

        {!data ? (
          <Skeleton className="h-56 w-full" />
        ) : (
          <>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {Object.entries(data.overview).map(([k, v]) => (
                <article key={k} className="card">
                  <p className="text-xs text-slate-500 uppercase">{k.replace('_', ' ')}</p>
                  <p className="text-2xl font-semibold">{v}</p>
                </article>
              ))}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="card h-72">
                <h3 className="font-semibold mb-2">Completion Mix</h3>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={chartData} dataKey="value" nameKey="name" outerRadius={96}>
                      {chartData.map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="card h-72">
                <h3 className="font-semibold mb-2">Avg Score per Team</h3>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.performance_snapshot.avg_score_per_team}>
                    <XAxis dataKey="team__name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="avg_score" fill="#0d9488" radius={6} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="card">
              <h3 className="font-semibold mb-3">Goal List</h3>
              <div className="space-y-3">
                {data.goals.map((g) => (
                  <article key={g.id} className="rounded-lg border p-3">
                    <div className="flex justify-between">
                      <h4 className="font-medium">{g.title}</h4>
                      <span className="badge bg-slate-100">{g.status}</span>
                    </div>
                    <div className="mt-2 h-2 w-full bg-slate-100 rounded-full">
                      <div className="h-2 rounded-full bg-accent transition-all duration-500" style={{ width: `${g.completion_percentage}%` }} />
                    </div>
                    <p className="text-xs mt-2 text-slate-500">Due: {g.due_date} {g.at_risk ? '• At risk' : ''}</p>
                  </article>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
