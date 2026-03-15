import { create } from 'zustand';
import { FilterState, PersonStatus, ScoreRange } from '../types/applicant';

interface RecruitmentState {
  filters: FilterState;
  selectedApplicants: string[];
  setFilters: (filters: Partial<FilterState>) => void;
  resetFilters: () => void;
  toggleApplicantSelection: (id: string) => void;
  selectAllApplicants: (ids: string[]) => void;
  clearSelection: () => void;
}

const defaultFilters: FilterState = {
  status: 'all',
  scoreRange: { min: 0, max: 100 },
  dateFrom: null,
  dateTo: null,
  search: '',
};

export const useRecruitmentStore = create<RecruitmentState>((set) => ({
  filters: defaultFilters,
  selectedApplicants: [],

  setFilters: (newFilters) =>
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
    })),

  resetFilters: () =>
    set({
      filters: defaultFilters,
      selectedApplicants: [],
    }),

  toggleApplicantSelection: (id) =>
    set((state) => ({
      selectedApplicants: state.selectedApplicants.includes(id)
        ? state.selectedApplicants.filter((a) => a !== id)
        : [...state.selectedApplicants, id],
    })),

  selectAllApplicants: (ids) =>
    set((state) => ({
      selectedApplicants: [...new Set([...state.selectedApplicants, ...ids])],
    })),

  clearSelection: () =>
    set({
      selectedApplicants: [],
    }),
}));

// Status color mapping
export const statusColors: Record<PersonStatus, { bg: string; text: string; label: string }> = {
  active: { bg: 'bg-emerald-500/20', text: 'text-emerald-400', label: 'Aktiv' },
  onboarding: { bg: 'bg-blue-500/20', text: 'text-blue-400', label: 'Onboarding' },
  offboarding: { bg: 'bg-amber-500/20', text: 'text-amber-400', label: 'Offboarding' },
  archived: { bg: 'bg-gray-500/20', text: 'text-gray-400', label: 'Archiviert' },
};

// Score color mapping
export const getScoreColor = (score: number | null): string => {
  if (score === null) return 'text-gray-400';
  if (score >= 80) return 'text-emerald-400';
  if (score >= 60) return 'text-blue-400';
  if (score >= 40) return 'text-amber-400';
  return 'text-red-400';
};

export const getScoreBadgeColor = (score: number | null): string => {
  if (score === null) return 'bg-gray-500/20 text-gray-400';
  if (score >= 80) return 'bg-emerald-500/20 text-emerald-400';
  if (score >= 60) return 'bg-blue-500/20 text-blue-400';
  if (score >= 40) return 'bg-amber-500/20 text-amber-400';
  return 'bg-red-500/20 text-red-400';
};
