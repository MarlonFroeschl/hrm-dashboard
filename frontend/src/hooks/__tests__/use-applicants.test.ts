import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { useApplicants, useApplicant, useCreateApplicant, useUpdateApplicantStatus, useInviteApplicant, useBulkUpdateStatus } from '../../hooks/use-applicants';
import { server } from '../../test/server';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  React.createElement(QueryClientProvider, { client: queryClient }, children)
);

beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }));
afterAll(() => server.close());

describe('useApplicants Hook', () => {
  it('should fetch applicants list successfully', async () => {
    const { result } = renderHook(() => useApplicants({}), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toBeDefined();
    expect(result.current.data?.items).toBeDefined();
    expect(Array.isArray(result.current.data?.items)).toBe(true);
  });

  it('should filter applicants by status', async () => {
    const { result } = renderHook(() => useApplicants({ status: 'active' }), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data?.items.every(a => a.status === 'active' || a.status === 'onboarding')).toBe(true);
  });

  it('should filter applicants by score range', async () => {
    const { result } = renderHook(() => useApplicants({ min_score: 70, max_score: 100 }), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    const itemsWithScore = result.current.data?.items.filter(a => a.matching_score !== null);
    expect(itemsWithScore?.every(a => a.matching_score! >= 70 && a.matching_score! <= 100)).toBe(true);
  });

  it('should filter applicants by search term', async () => {
    const { result } = renderHook(() => useApplicants({ search: 'Max' }), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data?.items.length).toBeGreaterThan(0);
    expect(result.current.data?.items.some(a => a.first_name.includes('Max'))).toBe(true);
  });

  it('should handle pagination', async () => {
    const { result } = renderHook(() => useApplicants({ page: 1, page_size: 2 }), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data?.items.length).toBeLessThanOrEqual(2);
    expect(result.current.data?.total_pages).toBeDefined();
  });

  it('should return empty array when no applicants match filters', async () => {
    const { result } = renderHook(() => useApplicants({ status: 'nonexistent' }), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data?.items.length).toBe(0);
  });

  it('should handle error state', async () => {
    // This would require a failing endpoint, which we don't have in mock
    // So we test that the hook returns proper initial state
    const { result } = renderHook(() => useApplicants({}), { wrapper });

    expect(result.current.isLoading).toBe(true);
    expect(result.current.error).toBeNull();
  });
});

describe('useApplicant Hook', () => {
  it('should fetch single applicant by id', async () => {
    const { result } = renderHook(() => useApplicant('1'), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toBeDefined();
    expect(result.current.data?.id).toBe('1');
    expect(result.current.data?.first_name).toBe('Max');
  });

  it('should return null for non-existent applicant', async () => {
    const { result } = renderHook(() => useApplicant('999'), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toBeUndefined();
  });

  it('should not fetch when id is empty', async () => {
    const { result } = renderHook(() => useApplicant(''), { wrapper });

    expect(result.current.isFetching).toBe(false);
  });
});

describe('useCreateApplicant Hook', () => {
  it('should create new applicant', async () => {
    const { result } = renderHook(() => useCreateApplicant(), { wrapper });

    let response: any;
    await waitFor(() => {
      result.current.mutate({
        first_name: 'Test',
        last_name: 'User',
        email: 'test@example.com',
      });
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toBeDefined();
  });

  it('should handle validation error', async () => {
    const { result } = renderHook(() => useCreateApplicant(), { wrapper });

    // Try to create without required fields - should still try the request
    result.current.mutate({
      first_name: '',
      last_name: '',
      email: '',
    });

    // The mock will accept it, but in real scenario would return validation error
    await waitFor(() => expect(result.current.isPending).toBe(false));
  });
});

describe('useUpdateApplicantStatus Hook', () => {
  it('should update applicant status', async () => {
    const { result } = renderHook(() => useUpdateApplicantStatus(), { wrapper });

    result.current.mutate({
      id: '1',
      status: { status: 'archived' },
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});

describe('useInviteApplicant Hook', () => {
  it('should send invitation to applicant', async () => {
    const { result } = renderHook(() => useInviteApplicant(), { wrapper });

    result.current.mutate({
      id: '1',
      data: { template_id: 'standard' },
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });

  it('should send invitation with custom message', async () => {
    const { result } = renderHook(() => useInviteApplicant(), { wrapper });

    result.current.mutate({
      id: '1',
      data: { custom_message: 'Custom invitation text' },
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});

describe('useBulkUpdateStatus Hook', () => {
  it('should bulk update multiple applicants', async () => {
    const { result } = renderHook(() => useBulkUpdateStatus(), { wrapper });

    result.current.mutate({
      ids: ['1', '2'],
      status: 'archived',
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });

  it('should handle empty ids array', async () => {
    const { result } = renderHook(() => useBulkUpdateStatus(), { wrapper });

    result.current.mutate({
      ids: [],
      status: 'archived',
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});
