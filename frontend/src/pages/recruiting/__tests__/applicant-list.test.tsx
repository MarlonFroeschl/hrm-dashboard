import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ApplicantListPage } from '../applicant-list';
import { useRecruitmentStore } from '../../../stores/recruitment-store';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  </BrowserRouter>
);

describe('ApplicantListPage', () => {
  beforeEach(() => {
    useRecruitmentStore.getState().clearSelection();
    useRecruitmentStore.getState().resetFilters();
  });

  it('should render page header', () => {
    render(<ApplicantListPage />, { wrapper });

    // Check header exists - will show loading state initially
    expect(screen.getByText('Bewerber')).toBeInTheDocument();
  });

  it('should render "Neuer Bewerber" button', () => {
    render(<ApplicantListPage />, { wrapper });

    expect(screen.getByText('Neuer Bewerber')).toBeInTheDocument();
  });

  it('should render search input', () => {
    render(<ApplicantListPage />, { wrapper });

    expect(screen.getByPlaceholderText('Bewerber suchen...')).toBeInTheDocument();
  });

  it('should render filter button', () => {
    render(<ApplicantListPage />, { wrapper });

    expect(screen.getByText('Filter')).toBeInTheDocument();
  });

  it('should render table headers', () => {
    render(<ApplicantListPage />, { wrapper });

    // Table headers are always rendered
    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Rolle')).toBeInTheDocument();
    expect(screen.getByText('Score')).toBeInTheDocument();
    expect(screen.getByText('Status')).toBeInTheDocument();
    expect(screen.getByText('Datum')).toBeInTheDocument();
    expect(screen.getByText('Aktionen')).toBeInTheDocument();
  });
});
