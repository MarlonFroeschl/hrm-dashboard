import { describe, it, expect, beforeEach } from 'vitest';
import { useRecruitmentStore, statusColors, getScoreColor, getScoreBadgeColor } from '../recruitment-store';

describe('recruitmentStore', () => {
  beforeEach(() => {
    useRecruitmentStore.getState().resetFilters();
    useRecruitmentStore.getState().clearSelection();
  });

  describe('Initial State', () => {
    it('should have default filters', () => {
      const { filters } = useRecruitmentStore.getState();

      expect(filters.status).toBe('all');
      expect(filters.scoreRange.min).toBe(0);
      expect(filters.scoreRange.max).toBe(100);
      expect(filters.dateFrom).toBeNull();
      expect(filters.dateTo).toBeNull();
      expect(filters.search).toBe('');
    });

    it('should have empty selected applicants', () => {
      const { selectedApplicants } = useRecruitmentStore.getState();

      expect(selectedApplicants).toEqual([]);
    });
  });

  describe('setFilters', () => {
    it('should update status filter', () => {
      const { setFilters } = useRecruitmentStore.getState();

      setFilters({ status: 'active' });

      expect(useRecruitmentStore.getState().filters.status).toBe('active');
    });

    it('should update score range', () => {
      const { setFilters } = useRecruitmentStore.getState();

      setFilters({ scoreRange: { min: 50, max: 80 } });

      const { filters } = useRecruitmentStore.getState();
      expect(filters.scoreRange.min).toBe(50);
      expect(filters.scoreRange.max).toBe(80);
    });

    it('should update date from', () => {
      const { setFilters } = useRecruitmentStore.getState();

      setFilters({ dateFrom: '2024-01-01' });

      expect(useRecruitmentStore.getState().filters.dateFrom).toBe('2024-01-01');
    });

    it('should update date to', () => {
      const { setFilters } = useRecruitmentStore.getState();

      setFilters({ dateTo: '2024-12-31' });

      expect(useRecruitmentStore.getState().filters.dateTo).toBe('2024-12-31');
    });

    it('should update search', () => {
      const { setFilters } = useRecruitmentStore.getState();

      setFilters({ search: 'Max' });

      expect(useRecruitmentStore.getState().filters.search).toBe('Max');
    });

    it('should merge partial filters', () => {
      const { setFilters } = useRecruitmentStore.getState();

      setFilters({ status: 'active' });
      setFilters({ search: 'test' });

      const { filters } = useRecruitmentStore.getState();
      expect(filters.status).toBe('active');
      expect(filters.search).toBe('test');
    });
  });

  describe('resetFilters', () => {
    it('should reset all filters to default', () => {
      const { setFilters, resetFilters } = useRecruitmentStore.getState();

      setFilters({ status: 'active', search: 'test', scoreRange: { min: 30, max: 70 } });
      resetFilters();

      const { filters } = useRecruitmentStore.getState();
      expect(filters.status).toBe('all');
      expect(filters.search).toBe('');
      expect(filters.scoreRange.min).toBe(0);
      expect(filters.scoreRange.max).toBe(100);
    });

    it('should clear selection on reset', () => {
      const { toggleApplicantSelection, resetFilters } = useRecruitmentStore.getState();

      toggleApplicantSelection('1');
      expect(useRecruitmentStore.getState().selectedApplicants).toContain('1');

      resetFilters();
      expect(useRecruitmentStore.getState().selectedApplicants).toEqual([]);
    });
  });

  describe('toggleApplicantSelection', () => {
    it('should add applicant to selection', () => {
      const { toggleApplicantSelection } = useRecruitmentStore.getState();

      toggleApplicantSelection('1');

      expect(useRecruitmentStore.getState().selectedApplicants).toContain('1');
    });

    it('should remove applicant from selection when already selected', () => {
      const { toggleApplicantSelection } = useRecruitmentStore.getState();

      toggleApplicantSelection('1');
      toggleApplicantSelection('1');

      expect(useRecruitmentStore.getState().selectedApplicants).not.toContain('1');
    });

    it('should handle multiple selections', () => {
      const { toggleApplicantSelection } = useRecruitmentStore.getState();

      toggleApplicantSelection('1');
      toggleApplicantSelection('2');
      toggleApplicantSelection('3');

      const { selectedApplicants } = useRecruitmentStore.getState();
      expect(selectedApplicants).toHaveLength(3);
      expect(selectedApplicants).toContain('1');
      expect(selectedApplicants).toContain('2');
      expect(selectedApplicants).toContain('3');
    });

    it('should not duplicate selections', () => {
      const { toggleApplicantSelection } = useRecruitmentStore.getState();

      toggleApplicantSelection('1');
      toggleApplicantSelection('1');
      toggleApplicantSelection('1');

      expect(useRecruitmentStore.getState().selectedApplicants).toHaveLength(1);
    });
  });

  describe('selectAllApplicants', () => {
    it('should add multiple applicants to selection', () => {
      const { selectAllApplicants } = useRecruitmentStore.getState();

      selectAllApplicants(['1', '2', '3']);

      const { selectedApplicants } = useRecruitmentStore.getState();
      expect(selectedApplicants).toHaveLength(3);
    });

    it('should merge with existing selections', () => {
      const { toggleApplicantSelection, selectAllApplicants } = useRecruitmentStore.getState();

      toggleApplicantSelection('1');
      selectAllApplicants(['2', '3']);

      const { selectedApplicants } = useRecruitmentStore.getState();
      expect(selectedApplicants).toHaveLength(3);
      expect(selectedApplicants).toContain('1');
    });

    it('should handle duplicates', () => {
      const { selectAllApplicants } = useRecruitmentStore.getState();

      selectAllApplicants(['1', '2', '1']);

      expect(useRecruitmentStore.getState().selectedApplicants).toHaveLength(2);
    });
  });

  describe('clearSelection', () => {
    it('should clear all selections', () => {
      const { toggleApplicantSelection, clearSelection } = useRecruitmentStore.getState();

      toggleApplicantSelection('1');
      toggleApplicantSelection('2');
      clearSelection();

      expect(useRecruitmentStore.getState().selectedApplicants).toEqual([]);
    });
  });
});

describe('statusColors', () => {
  it('should have correct colors for active', () => {
    expect(statusColors.active).toEqual({
      bg: 'bg-emerald-500/20',
      text: 'text-emerald-400',
      label: 'Aktiv',
    });
  });

  it('should have correct colors for onboarding', () => {
    expect(statusColors.onboarding).toEqual({
      bg: 'bg-blue-500/20',
      text: 'text-blue-400',
      label: 'Onboarding',
    });
  });

  it('should have correct colors for offboarding', () => {
    expect(statusColors.offboarding).toEqual({
      bg: 'bg-amber-500/20',
      text: 'text-amber-400',
      label: 'Offboarding',
    });
  });

  it('should have correct colors for archived', () => {
    expect(statusColors.archived).toEqual({
      bg: 'bg-gray-500/20',
      text: 'text-gray-400',
      label: 'Archiviert',
    });
  });
});

describe('getScoreColor', () => {
  it('should return gray for null', () => {
    expect(getScoreColor(null)).toBe('text-gray-400');
  });

  it('should return emerald for 80+', () => {
    expect(getScoreColor(80)).toBe('text-emerald-400');
    expect(getScoreColor(90)).toBe('text-emerald-400');
    expect(getScoreColor(100)).toBe('text-emerald-400');
  });

  it('should return blue for 60-79', () => {
    expect(getScoreColor(60)).toBe('text-blue-400');
    expect(getScoreColor(70)).toBe('text-blue-400');
    expect(getScoreColor(79)).toBe('text-blue-400');
  });

  it('should return amber for 40-59', () => {
    expect(getScoreColor(40)).toBe('text-amber-400');
    expect(getScoreColor(50)).toBe('text-amber-400');
    expect(getScoreColor(59)).toBe('text-amber-400');
  });

  it('should return red for below 40', () => {
    expect(getScoreColor(0)).toBe('text-red-400');
    expect(getScoreColor(20)).toBe('text-red-400');
    expect(getScoreColor(39)).toBe('text-red-400');
  });
});

describe('getScoreBadgeColor', () => {
  it('should return gray badge for null', () => {
    expect(getScoreBadgeColor(null)).toBe('bg-gray-500/20 text-gray-400');
  });

  it('should return emerald badge for 80+', () => {
    expect(getScoreBadgeColor(80)).toBe('bg-emerald-500/20 text-emerald-400');
  });

  it('should return blue badge for 60-79', () => {
    expect(getScoreBadgeColor(60)).toBe('bg-blue-500/20 text-blue-400');
  });

  it('should return amber badge for 40-59', () => {
    expect(getScoreBadgeColor(40)).toBe('bg-amber-500/20 text-amber-400');
  });

  it('should return red badge for below 40', () => {
    expect(getScoreBadgeColor(20)).toBe('bg-red-500/20 text-red-400');
  });
});
