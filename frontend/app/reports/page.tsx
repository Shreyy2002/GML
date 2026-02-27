'use client';

import AppShell from '@/components/AppShell';
import { api } from '@/lib/api';
import { storage } from '@/lib/storage';

async function download(path: string, filename: string) {
  const response = await api.get(path, { responseType: 'blob' });
  const url = window.URL.createObjectURL(response.data);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}

export default function ReportsPage() {
  const role = storage.getUser()?.role;

  return (
    <AppShell>
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Reports</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <article className="card">
            <h3 className="font-semibold">Individual Report</h3>
            <div className="mt-3 flex gap-2">
              <button className="rounded bg-ink text-white px-3 py-1" onClick={() => download('/reports/individual/?format=csv', 'individual_report.csv')}>CSV</button>
              <button className="rounded bg-accent text-white px-3 py-1" onClick={() => download('/reports/individual/?format=pdf', 'individual_report.pdf')}>PDF</button>
            </div>
          </article>
          <article className="card">
            <h3 className="font-semibold">Team Report</h3>
            <div className="mt-3 flex gap-2">
              <button className="rounded bg-ink text-white px-3 py-1" onClick={() => download('/reports/team/?team_id=1&format=csv', 'team_report.csv')}>CSV</button>
              <button className="rounded bg-accent text-white px-3 py-1" onClick={() => download('/reports/team/?team_id=1&format=pdf', 'team_report.pdf')}>PDF</button>
            </div>
          </article>
          <article className={`card ${role !== 'ADMIN' ? 'opacity-60' : ''}`}>
            <h3 className="font-semibold">Company Report</h3>
            <div className="mt-3 flex gap-2">
              <button disabled={role !== 'ADMIN'} className="rounded bg-ink text-white px-3 py-1 disabled:opacity-40" onClick={() => download('/reports/company/?format=csv', 'company_report.csv')}>CSV</button>
              <button disabled={role !== 'ADMIN'} className="rounded bg-accent text-white px-3 py-1 disabled:opacity-40" onClick={() => download('/reports/company/?format=pdf', 'company_report.pdf')}>PDF</button>
            </div>
          </article>
        </div>
      </div>
    </AppShell>
  );
}
