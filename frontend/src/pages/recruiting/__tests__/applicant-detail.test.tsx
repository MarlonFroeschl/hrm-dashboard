import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ApplicantDetailPage } from '../applicant-detail';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

describe('ApplicantDetailPage', () => {
  it('should render without crashing', () => {
    const { container } = render(
      <MemoryRouter initialEntries={['/recruiting/1']}>
        <QueryClientProvider client={queryClient}>
          <Routes>
            <Route path="/recruiting/:id" element={<ApplicantDetailPage />} />
          </Routes>
        </QueryClientProvider>
      </MemoryRouter>
    );

    // Basic render test - component renders in loading or error state initially
    expect(container).toBeInTheDocument();
  });
});
