import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../utils/api';
import {
  Applicant,
  ApplicantFilters,
  PaginatedResponse,
  CreateApplicantRequest,
  UpdateStatusRequest,
  InviteRequest,
  CVUploadResponse,
} from '../types/applicant';

// Query Keys
export const applicantKeys = {
  all: ['applicants'] as const,
  lists: () => [...applicantKeys.all, 'list'] as const,
  list: (filters: ApplicantFilters) => [...applicantKeys.lists(), filters] as const,
  details: () => [...applicantKeys.all, 'detail'] as const,
  detail: (id: string) => [...applicantKeys.details(), id] as const,
};

// Fetch Applicants List
export function useApplicants(filters: ApplicantFilters) {
  return useQuery({
    queryKey: applicantKeys.list(filters),
    queryFn: async () => {
      const params = new URLSearchParams();

      if (filters.status && filters.status !== 'all' && filters.status !== undefined) params.append('status', filters.status);
      if (filters.min_score !== undefined) params.append('min_score', String(filters.min_score));
      if (filters.max_score !== undefined) params.append('max_score', String(filters.max_score));
      if (filters.date_from) params.append('date_from', filters.date_from);
      if (filters.date_to) params.append('date_to', filters.date_to);
      if (filters.page) params.append('page', String(filters.page));
      if (filters.page_size) params.append('page_size', String(filters.page_size));
      if (filters.search) params.append('search', filters.search);

      return api.get<PaginatedResponse<Applicant>>(`/applicants?${params.toString()}`);
    },
  });
}

// Fetch Single Applicant
export function useApplicant(id: string) {
  return useQuery({
    queryKey: applicantKeys.detail(id),
    queryFn: () => api.get<Applicant>(`/applicants/${id}`),
    enabled: !!id,
  });
}

// Create Applicant
export function useCreateApplicant() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateApplicantRequest) => api.post<Applicant>('/applicants', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: applicantKeys.lists() });
    },
  });
}

// Update Applicant Status
export function useUpdateApplicantStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: UpdateStatusRequest }) =>
      api.patch<Applicant>(`/applicants/${id}/status`, status),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: applicantKeys.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: applicantKeys.lists() });
    },
  });
}

// Invite Applicant
export function useInviteApplicant() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data?: InviteRequest }) =>
      api.post(`/applicants/${id}/invite`, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: applicantKeys.detail(variables.id) });
    },
  });
}

// Upload CV
export function useUploadCV() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ personId, file }: { personId: string; file: File }) =>
      api.uploadFile<CVUploadResponse>('/applicants/upload-cv', file, { person_id: personId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: applicantKeys.lists() });
    },
  });
}

// Bulk Status Update
export function useBulkUpdateStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ ids, status }: { ids: string[]; status: UpdateStatusRequest['status'] }) =>
      api.post('/applicants/bulk-update', { ids, status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: applicantKeys.lists() });
    },
  });
}
