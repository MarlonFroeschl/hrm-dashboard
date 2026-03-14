import { useState } from 'react';
import { useParams, useNavigate, Navigate } from 'react-router-dom';
import {
  ArrowLeft,
  Mail,
  Phone,
  Calendar,
  FileText,
  User,
  Award,
  Send,
  Download,
  ExternalLink,
} from 'lucide-react';
import { Button, Badge, Tabs, TabsList, TabsTrigger, TabsContent, CardSkeleton } from '../../components/ui';
import { ScoreRing } from '../../components/charts/score-ring';
import { StatusTimeline } from '../../components/charts/status-timeline';
import { SkillsCloud } from '../../components/charts/skills-cloud';
import { CVUpload } from '../../components/forms/cv-upload';
import { InviteModal } from '../../components/forms/invite-modal';
import { useApplicant, useInviteApplicant, useUploadCV } from '../../hooks/use-applicants';
import { statusColors, getScoreBadgeColor } from '../../stores/recruitment-store';

// UUID regex pattern for validation
const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export function ApplicantDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'processing' | 'completed' | 'failed'>('idle');

  // Validate UUID from route params - redirect if invalid
  if (!id || !UUID_REGEX.test(id)) {
    return <Navigate to="/recruiting" replace />;
  }

  const { data: applicant, isLoading, error } = useApplicant(id);
  const inviteMutation = useInviteApplicant();
  const uploadMutation = useUploadCV();

  const handleInvite = async (templateId?: string, customMessage?: string) => {
    if (!id) return;
    await inviteMutation.mutateAsync({ id, data: { template_id: templateId, custom_message: customMessage } });
  };

  const handleUpload = async (file: File) => {
    if (!id) return;
    setUploadStatus('uploading');
    try {
      await uploadMutation.mutateAsync({ personId: id, file });
      setUploadStatus('completed');
    } catch {
      setUploadStatus('failed');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
        <div className="max-w-5xl mx-auto">
          <CardSkeleton />
        </div>
      </div>
    );
  }

  if (error || !applicant) {
    return (
      <div className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
        <div className="max-w-5xl mx-auto text-center">
          <p className="text-red-400">Bewerber nicht gefunden</p>
          <Button variant="outline" className="mt-4" onClick={() => navigate('/recruiting')}>
            Zurück zur Liste
          </Button>
        </div>
      </div>
    );
  }

  const skills = applicant.extracted_data?.skills
    ? [
        ...applicant.extracted_data.skills.technical.map((s) => ({ name: s, matched: true })),
        ...applicant.extracted_data.skills.soft.map((s) => ({ name: s, matched: false })),
      ]
    : [];

  const timelineEvents = [
    { status: 'active' as const, label: 'Bewerbung', timestamp: applicant.created_at, completed: true },
    { status: 'onboarding' as const, label: 'Onboarding', completed: applicant.status === 'onboarding' || applicant.status === 'active' },
    { status: 'offboarding' as const, label: 'Offboarding', completed: applicant.status === 'offboarding' || applicant.status === 'archived' },
    { status: 'archived' as const, label: 'Abgeschlossen', completed: applicant.status === 'archived' },
  ];

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Back Button */}
        <Button variant="ghost" onClick={() => navigate('/recruiting')}>
          <ArrowLeft className="w-4 h-4" />
          Zurück zur Liste
        </Button>

        {/* Header Card */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-6">
              <ScoreRing score={applicant.matching_score} size="lg" />
              <div>
                <h1 className="text-2xl font-bold text-zinc-100">
                  {applicant.first_name} {applicant.last_name}
                </h1>
                <div className="flex items-center gap-4 mt-2">
                  <span className="flex items-center gap-1.5 text-sm text-zinc-400">
                    <Mail className="w-4 h-4" />
                    {applicant.email}
                  </span>
                  {applicant.phone && (
                    <span className="flex items-center gap-1.5 text-sm text-zinc-400">
                      <Phone className="w-4 h-4" />
                      {applicant.phone}
                    </span>
                  )}
                  <span className="flex items-center gap-1.5 text-sm text-zinc-400">
                    <Calendar className="w-4 h-4" />
                    {new Date(applicant.created_at).toLocaleDateString('de-DE')}
                  </span>
                </div>
                <div className="flex items-center gap-2 mt-3">
                  <span
                    className={`px-2.5 py-1 rounded-full text-xs font-medium ${getScoreBadgeColor(applicant.matching_score)}`}
                  >
                    Match: {applicant.matching_score !== null ? `${applicant.matching_score}%` : 'N/A'}
                  </span>
                  <span
                    className={`px-2.5 py-1 rounded-full text-xs font-medium ${statusColors[applicant.status].bg} ${statusColors[applicant.status].text}`}
                  >
                    {statusColors[applicant.status].label}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex gap-3">
              <Button variant="outline" onClick={() => setShowInviteModal(true)}>
                <Send className="w-4 h-4" />
                Einladen
              </Button>
            </div>
          </div>

          {/* Status Timeline */}
          <div className="mt-8 pt-6 border-t border-zinc-800">
            <StatusTimeline currentStatus={applicant.status} events={timelineEvents} />
          </div>
        </div>

        {/* Tabs Content */}
        <Tabs defaultValue="profile" className="space-y-6">
          <TabsList>
            <TabsTrigger value="profile">
              <User className="w-4 h-4 mr-2" />
              Profil
            </TabsTrigger>
            <TabsTrigger value="cv">
              <FileText className="w-4 h-4 mr-2" />
              CV-Vorschau
            </TabsTrigger>
            <TabsTrigger value="skills">
              <Award className="w-4 h-4 mr-2" />
              Skills
            </TabsTrigger>
          </TabsList>

          <TabsContent value="profile">
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-zinc-100 mb-4">Persönliche Daten</h3>
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <label className="text-sm text-zinc-500">Vorname</label>
                    <p className="text-zinc-200">{applicant.first_name}</p>
                  </div>
                  <div>
                    <label className="text-sm text-zinc-500">Nachname</label>
                    <p className="text-zinc-200">{applicant.last_name}</p>
                  </div>
                  <div>
                    <label className="text-sm text-zinc-500">E-Mail</label>
                    <p className="text-zinc-200">{applicant.email}</p>
                  </div>
                  <div>
                    <label className="text-sm text-zinc-500">Telefon</label>
                    <p className="text-zinc-200">{applicant.phone || '-'}</p>
                  </div>
                </div>
              </div>

              {applicant.extracted_data?.summary && (
                <div>
                  <h3 className="text-lg font-semibold text-zinc-100 mb-4">Zusammenfassung</h3>
                  <p className="text-zinc-300 leading-relaxed">{applicant.extracted_data.summary}</p>
                </div>
              )}

              {applicant.extracted_data?.experience && applicant.extracted_data.experience.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-zinc-100 mb-4">Berufserfahrung</h3>
                  <div className="space-y-4">
                    {applicant.extracted_data.experience.map((exp, index) => (
                      <div key={index} className="border-l-2 border-zinc-700 pl-4">
                        <p className="font-medium text-zinc-100">{exp.role}</p>
                        <p className="text-sm text-zinc-400">{exp.company}</p>
                        <p className="text-xs text-zinc-500">{exp.duration}</p>
                        <p className="text-sm text-zinc-300 mt-2">{exp.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {applicant.extracted_data?.education && applicant.extracted_data.education.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-zinc-100 mb-4">Ausbildung</h3>
                  <div className="space-y-4">
                    {applicant.extracted_data.education.map((edu, index) => (
                      <div key={index} className="border-l-2 border-zinc-700 pl-4">
                        <p className="font-medium text-zinc-100">{edu.degree}</p>
                        <p className="text-sm text-zinc-400">{edu.institution}</p>
                        <p className="text-xs text-zinc-500">
                          {edu.field} - {edu.year}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="cv">
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-zinc-100 mb-6">Lebenslauf</h3>

              {applicant.documents && applicant.documents.length > 0 ? (
                <div className="space-y-4">
                  {applicant.documents.map((doc) => (
                    <div
                      key={doc.id}
                      className="flex items-center justify-between p-4 bg-zinc-800/50 border border-zinc-700 rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <FileText className="w-8 h-8 text-blue-400" />
                        <div>
                          <p className="font-medium text-zinc-200">{doc.file_name}</p>
                          <p className="text-xs text-zinc-500">
                            Hochgeladen am {new Date(doc.uploaded_at).toLocaleDateString('de-DE')}
                          </p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm">
                          <ExternalLink className="w-4 h-4" />
                          Vorschau
                        </Button>
                        <Button variant="outline" size="sm">
                          <Download className="w-4 h-4" />
                          Download
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <CVUpload onUpload={handleUpload} status={uploadStatus} />
              )}
            </div>
          </TabsContent>

          <TabsContent value="skills">
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-zinc-100 mb-6">Skills & Kompetenzen</h3>
              <SkillsCloud skills={skills} />
            </div>
          </TabsContent>
        </Tabs>

        {/* Invite Modal */}
        <InviteModal
          isOpen={showInviteModal}
          onClose={() => setShowInviteModal(false)}
          onInvite={handleInvite}
          applicantName={`${applicant.first_name} ${applicant.last_name}`}
          loading={inviteMutation.isPending}
        />
      </div>
    </div>
  );
}
