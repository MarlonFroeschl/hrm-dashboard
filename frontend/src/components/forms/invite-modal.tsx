import { useState } from 'react';
import { Mail, Send } from 'lucide-react';
import { Modal, Button, Input, Textarea } from '../ui';

interface InviteModalProps {
  isOpen: boolean;
  onClose: () => void;
  onInvite: (templateId?: string, customMessage?: string) => Promise<void>;
  applicantName: string;
  loading?: boolean;
}

const templates = [
  {
    id: 'standard',
    label: 'Standard',
    subject: 'Einladung zum Vorstellungsgespräch',
    preview: 'Sehr geehrte/r ...,\n\nwir freuen uns, Sie zu einem Vorstellungsgespräch einladen zu dürfen...',
  },
  {
    id: 'technical',
    label: 'Technisches Interview',
    subject: 'Einladung zum technischen Interview',
    preview: 'Sehr geehrte/r ...,\n\nwir würden Sie gerne zu einem technischen Interview einladen...',
  },
  {
    id: 'custom',
    label: 'Individuell',
    subject: '',
    preview: '',
  },
];

export function InviteModal({ isOpen, onClose, onInvite, applicantName, loading }: InviteModalProps) {
  const [selectedTemplate, setSelectedTemplate] = useState('standard');
  const [customMessage, setCustomMessage] = useState('');
  const [subject, setSubject] = useState(templates[0]?.subject ?? '');

  const handleSubmit = async () => {
    await onInvite(selectedTemplate === 'custom' ? undefined : selectedTemplate, customMessage || undefined);
    onClose();
  };

  const handleTemplateChange = (templateId: string) => {
    setSelectedTemplate(templateId);
    const template = templates.find((t) => t.id === templateId);
    if (template) {
      setSubject(template.subject);
      if (templateId !== 'custom' && template.preview) {
        setCustomMessage(template.preview);
      }
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Bewerber einladen" size="lg">
      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-3">
            E-Mail-Vorlage auswählen
          </label>
          <div className="grid grid-cols-3 gap-3">
            {templates.map((template) => (
              <button
                key={template.id}
                onClick={() => handleTemplateChange(template.id)}
                className={`p-3 rounded-lg border text-left transition-all ${
                  selectedTemplate === template.id
                    ? 'border-blue-500 bg-blue-500/10 text-zinc-100'
                    : 'border-zinc-700 bg-zinc-800/50 text-zinc-400 hover:border-zinc-600'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  <span className="text-sm font-medium">{template.label}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        <Input
          label="Betreff"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          placeholder="Betreff der E-Mail"
        />

        <Textarea
          label="Nachricht"
          value={customMessage}
          onChange={(e) => setCustomMessage(e.target.value)}
          placeholder="Individuelle Nachricht..."
          rows={8}
        />

        <div className="flex items-center justify-between pt-4 border-t border-zinc-800">
          <p className="text-sm text-zinc-500">
            Einladung wird an <span className="text-zinc-300">{applicantName}</span> gesendet
          </p>
          <div className="flex gap-3">
            <Button variant="ghost" onClick={onClose}>
              Abbrechen
            </Button>
            <Button onClick={handleSubmit} loading={loading}>
              <Send className="w-4 h-4" />
              Einladung senden
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
}
