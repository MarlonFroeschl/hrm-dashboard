import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, CheckCircle2, Loader2, XCircle, AlertCircle } from 'lucide-react';
import { clsx } from 'clsx';
import { Button } from '../ui/button';

type UploadStatus = 'idle' | 'uploading' | 'processing' | 'completed' | 'failed';

interface CVUploadProps {
  onUpload: (file: File) => Promise<void>;
  status?: UploadStatus;
  progress?: number;
  error?: string;
}

interface UploadStep {
  label: string;
  status: 'pending' | 'active' | 'completed' | 'error';
}

const steps: UploadStep[] = [
  { label: 'Hochladen', status: 'pending' },
  { label: 'OCR', status: 'pending' },
  { label: 'KI-Analyse', status: 'pending' },
  { label: 'Fertig', status: 'pending' },
];

function StepIndicator({ steps, currentStep }: { steps: UploadStep[]; currentStep: number }) {
  return (
    <div className="flex items-center justify-between w-full max-w-md">
      {steps.map((step, index) => (
        <div key={step.label} className="flex items-center">
          <div className="flex flex-col items-center">
            <div
              className={clsx(
                'w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300',
                step.status === 'completed'
                  ? 'bg-emerald-500/20 text-emerald-400'
                  : step.status === 'active'
                  ? 'bg-blue-500/20 text-blue-400'
                  : step.status === 'error'
                  ? 'bg-red-500/20 text-red-400'
                  : 'bg-zinc-800 text-zinc-500'
              )}
            >
              {step.status === 'completed' && <CheckCircle2 className="w-5 h-5" />}
              {step.status === 'active' && <Loader2 className="w-5 h-5 animate-spin" />}
              {step.status === 'error' && <XCircle className="w-5 h-5" />}
              {step.status === 'pending' && <span className="text-xs font-medium">{index + 1}</span>}
            </div>
            <span className="text-xs mt-1 text-zinc-500">{step.label}</span>
          </div>
          {index < steps.length - 1 && (
            <div
              className={clsx(
                'w-12 h-0.5 mx-2',
                index < currentStep ? 'bg-emerald-500' : 'bg-zinc-700'
              )}
            />
          )}
        </div>
      ))}
    </div>
  );
}

export function CVUpload({ onUpload, status = 'idle', error }: CVUploadProps) {
  const [file, setFile] = useState<File | null>(null);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const uploadedFile = acceptedFiles[0];
      if (uploadedFile && uploadedFile.type === 'application/pdf') {
        setFile(uploadedFile);
        await onUpload(uploadedFile);
      }
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    disabled: status === 'uploading' || status === 'processing',
  });

  const getCurrentStep = (): number => {
    switch (status) {
      case 'uploading':
        return 0;
      case 'processing':
        return 1;
      case 'completed':
        return 3;
      case 'failed':
        return -1;
      default:
        return -1;
    }
  };

  const currentStep = getCurrentStep();

  return (
    <div className="space-y-6">
      {status === 'idle' && (
        <div
          {...getRootProps()}
          className={clsx(
            'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200',
            isDragActive
              ? 'border-blue-500 bg-blue-500/10'
              : 'border-zinc-700 hover:border-zinc-600 hover:bg-zinc-800/50'
          )}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-zinc-800 flex items-center justify-center">
              <Upload className="w-6 h-6 text-zinc-400" />
            </div>
            <div>
              <p className="text-sm font-medium text-zinc-200">
                {isDragActive ? 'Datei hier ablegen' : 'PDF hierher ziehen oder klicken'}
              </p>
              <p className="text-xs text-zinc-500 mt-1">Max. 10MB, nur PDF</p>
            </div>
          </div>
        </div>
      )}

      {file && status !== 'idle' && (
        <div className="bg-zinc-800/50 border border-zinc-700 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
              <FileText className="w-5 h-5 text-blue-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-zinc-200 truncate">{file.name}</p>
              <p className="text-xs text-zinc-500">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>
        </div>
      )}

      {status !== 'idle' && status !== 'failed' && (
        <div className="py-4">
          <StepIndicator
            steps={steps.map((step, index) => ({
              ...step,
              status:
                index < currentStep
                  ? 'completed'
                  : index === currentStep
                  ? 'active'
                  : 'pending',
            }))}
            currentStep={currentStep}
          />
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-400" />
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      {status === 'completed' && (
        <div className="flex justify-center">
          <Button
            variant="outline"
            onClick={() => {
              setFile(null);
              window.location.reload();
            }}
          >
            Neuen Upload starten
          </Button>
        </div>
      )}
    </div>
  );
}
