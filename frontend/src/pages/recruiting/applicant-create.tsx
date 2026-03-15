import { useState } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { ArrowLeft, Save } from 'lucide-react';
import { Button, Input } from '../../components/ui';
import { useCreateApplicant } from '../../hooks/use-applicants';

export function ApplicantCreatePage() {
  const navigate = useNavigate();
  const createMutation = useCreateApplicant();
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.first_name.trim()) {
      newErrors.first_name = 'Vorname ist erforderlich';
    }
    if (!formData.last_name.trim()) {
      newErrors.last_name = 'Nachname ist erforderlich';
    }
    if (!formData.email.trim()) {
      newErrors.email = 'E-Mail ist erforderlich';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Ungültige E-Mail-Adresse';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    try {
      const result = await createMutation.mutateAsync(formData);
      navigate(`/recruiting/${result.id}`);
    } catch {
      // Error handling is done by react-query
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }));
    }
  };

  if (createMutation.isSuccess) {
    return <Navigate to="/recruiting" replace />;
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Back Button */}
        <Button variant="ghost" onClick={() => navigate('/recruiting')}>
          <ArrowLeft className="w-4 h-4" />
          Zurück zur Liste
        </Button>

        {/* Form Card */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h1 className="text-2xl font-bold text-zinc-100 mb-6">Neuen Bewerber anlegen</h1>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-2">
                  Vorname *
                </label>
                <Input
                  type="text"
                  value={formData.first_name}
                  onChange={(e) => handleChange('first_name', e.target.value)}
                  placeholder="Max"
                  error={errors.first_name}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-2">
                  Nachname *
                </label>
                <Input
                  type="text"
                  value={formData.last_name}
                  onChange={(e) => handleChange('last_name', e.target.value)}
                  placeholder="Mustermann"
                  error={errors.last_name}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">
                E-Mail *
              </label>
              <Input
                type="email"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                placeholder="max.mustermann@example.com"
                error={errors.email}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">
                Telefon
              </label>
              <Input
                type="tel"
                value={formData.phone}
                onChange={(e) => handleChange('phone', e.target.value)}
                placeholder="+43 123 456789"
              />
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <Button type="button" variant="outline" onClick={() => navigate('/recruiting')}>
                Abbrechen
              </Button>
              <Button type="submit" disabled={createMutation.isPending}>
                <Save className="w-4 h-4" />
                {createMutation.isPending ? 'Speichern...' : 'Bewerber anlegen'}
              </Button>
            </div>
          </form>

          {createMutation.isError && (
            <div className="mt-4 p-4 bg-red-900/20 border border-red-800 rounded-lg">
              <p className="text-sm text-red-400">
                Fehler beim Anlegen des Bewerbers. Bitte versuchen Sie es erneut.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
