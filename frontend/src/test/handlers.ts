import { http, HttpResponse, delay } from 'msw';
import { Applicant, PaginatedResponse } from '../../types/applicant';

// Mock data
export const mockApplicants: Applicant[] = [
  {
    id: '1',
    first_name: 'Max',
    last_name: 'Mustermann',
    email: 'max.mustermann@example.com',
    phone: '+49 123 456789',
    status: 'active',
    matching_score: 85,
    extracted_data: {
      skills: {
        technical: ['TypeScript', 'React', 'Node.js'],
        soft: ['Kommunikation', 'Teamwork'],
        languages: ['Deutsch', 'Englisch'],
      },
      experience: [
        {
          company: 'Tech Corp',
          role: 'Senior Developer',
          duration: '2020 - Present',
          description: 'Full-stack development',
        },
      ],
      education: [
        {
          institution: 'University of Berlin',
          degree: 'M.Sc.',
          field: 'Computer Science',
          year: '2019',
        },
      ],
      summary: 'Erfahrener Full-Stack Entwickler mit Fokus auf moderne Web-Technologien.',
    },
    created_at: '2024-01-15T10:00:00Z',
    documents: [
      {
        id: 'doc1',
        file_name: 'lebenslauf.pdf',
        file_type: 'application/pdf',
        file_path: '/uploads/cv1.pdf',
        uploaded_at: '2024-01-15T10:00:00Z',
      },
    ],
  },
  {
    id: '2',
    first_name: 'Anna',
    last_name: 'Schmidt',
    email: 'anna.schmidt@example.com',
    status: 'onboarding',
    matching_score: 72,
    extracted_data: {
      skills: {
        technical: ['Python', 'SQL', 'Docker'],
        soft: ['Projektmanagement'],
        languages: ['Deutsch', 'Englisch', 'Französisch'],
      },
      experience: [],
      education: [],
      summary: 'Data Analyst mit Erfahrung in Machine Learning.',
    },
    created_at: '2024-02-20T14:30:00Z',
    documents: [],
  },
  {
    id: '3',
    first_name: 'Johannes',
    last_name: 'Weber',
    email: 'johannes.weber@example.com',
    status: 'archived',
    matching_score: 45,
    extracted_data: null,
    created_at: '2023-11-05T09:15:00Z',
    documents: [],
  },
  {
    id: '4',
    first_name: 'Maria',
    last_name: 'Müller',
    email: 'maria.mueller@example.com',
    status: 'active',
    matching_score: null,
    extracted_data: {
      skills: { technical: [], soft: [], languages: [] },
      experience: [],
      education: [],
    },
    created_at: '2024-03-01T11:00:00Z',
    documents: [],
  },
];

export const handlers = [
  // GET /applicants - List applicants with filters
  http.get('/api/v1/applicants', async ({ request }) => {
    await delay(100);
    const url = new URL(request.url);
    const status = url.searchParams.get('status');
    const minScore = url.searchParams.get('min_score');
    const maxScore = url.searchParams.get('max_score');
    const search = url.searchParams.get('search');
    const page = parseInt(url.searchParams.get('page') || '1');
    const pageSize = parseInt(url.searchParams.get('page_size') || '10');

    let filtered = [...mockApplicants];

    // Apply filters
    if (status && status !== 'all') {
      filtered = filtered.filter(a => a.status === status);
    }
    if (minScore) {
      filtered = filtered.filter(a => a.matching_score !== null && a.matching_score >= parseInt(minScore));
    }
    if (maxScore) {
      filtered = filtered.filter(a => a.matching_score !== null && a.matching_score <= parseInt(maxScore));
    }
    if (search) {
      const searchLower = search.toLowerCase();
      filtered = filtered.filter(a =>
        a.first_name.toLowerCase().includes(searchLower) ||
        a.last_name.toLowerCase().includes(searchLower) ||
        a.email.toLowerCase().includes(searchLower)
      );
    }

    const total = filtered.length;
    const totalPages = Math.ceil(total / pageSize);
    const items = filtered.slice((page - 1) * pageSize, page * pageSize);

    return HttpResponse.json<PaginatedResponse<Applicant>>({
      items,
      total,
      page,
      page_size: pageSize,
      total_pages: totalPages,
    });
  }),

  // GET /applicants/:id - Get single applicant
  http.get('/api/v1/applicants/:id', async ({ params }) => {
    await delay(100);
    const applicant = mockApplicants.find(a => a.id === params.id);

    if (!applicant) {
      return new HttpResponse(null, { status: 404 });
    }

    return HttpResponse.json(applicant);
  }),

  // POST /applicants - Create applicant
  http.post('/api/v1/applicants', async ({ request }) => {
    await delay(100);
    const body = await request.json() as { first_name: string; last_name: string; email: string };

    const newApplicant: Applicant = {
      id: String(mockApplicants.length + 1),
      first_name: body.first_name,
      last_name: body.last_name,
      email: body.email,
      status: 'active',
      matching_score: null,
      extracted_data: null,
      created_at: new Date().toISOString(),
      documents: [],
    };

    mockApplicants.push(newApplicant);
    return HttpResponse.json(newApplicant, { status: 201 });
  }),

  // PATCH /applicants/:id/status - Update status
  http.patch('/api/v1/applicants/:id/status', async ({ params, request }) => {
    await delay(100);
    const body = await request.json() as { status: string };
    const applicant = mockApplicants.find(a => a.id === params.id);

    if (!applicant) {
      return new HttpResponse(null, { status: 404 });
    }

    applicant.status = body.status as Applicant['status'];
    return HttpResponse.json(applicant);
  }),

  // POST /applicants/:id/invite - Send invitation
  http.post('/api/v1/applicants/:id/invite', async ({ params }) => {
    await delay(200);
    const applicant = mockApplicants.find(a => a.id === params.id);

    if (!applicant) {
      return new HttpResponse(null, { status: 404 });
    }

    return HttpResponse.json({ success: true, message: 'Invitation sent' });
  }),

  // POST /applicants/upload-cv - Upload CV
  http.post('/api/v1/applicants/upload-cv', async ({ request }) => {
    await delay(500);
    return HttpResponse.json({
      id: 'new-doc-id',
      status: 'completed',
      message: 'CV uploaded and processed successfully',
    });
  }),

  // POST /applicants/bulk-update - Bulk status update
  http.post('/api/v1/applicants/bulk-update', async ({ request }) => {
    await delay(200);
    const body = await request.json() as { ids: string[]; status: string };

    body.ids.forEach(id => {
      const applicant = mockApplicants.find(a => a.id === id);
      if (applicant) {
        applicant.status = body.status as Applicant['status'];
      }
    });

    return HttpResponse.json({ success: true, updated: body.ids.length });
  }),
];
