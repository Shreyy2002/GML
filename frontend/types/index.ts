export type Role = 'TEAM_MEMBER' | 'EVALUATOR' | 'ADMIN';

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: Role;
}

export interface Goal {
  id: number;
  title: string;
  description: string;
  level: 'COMPANY' | 'TEAM' | 'INDIVIDUAL';
  status: 'DRAFT' | 'PENDING' | 'ACTIVE' | 'COMPLETED' | 'SCORED' | 'REJECTED';
  owner: number;
  evaluator: number | null;
  team: number | null;
  parent_goal: number | null;
  due_date: string;
  weightage: string;
  category: string;
  completion_percentage: number;
  final_score: string | null;
  at_risk: boolean;
  is_locked: boolean;
}

export interface DashboardResponse {
  overview: {
    total_goals: number;
    active_pct: number;
    completed_pct: number;
    pending_pct: number;
    rejected_pct: number;
  };
  status_breakdown: Record<string, number>;
  goals: Array<{ id: number; title: string; status: string; completion_percentage: number; due_date: string; at_risk: boolean }>;
  performance_snapshot: {
    avg_score_per_member: Array<{ owner__username: string; avg_score: number }>;
    avg_score_per_team: Array<{ team__name: string; avg_score: number }>;
  };
}
