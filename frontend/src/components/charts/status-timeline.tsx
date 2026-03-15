import { CheckCircle2, Circle, Clock } from 'lucide-react';
import { clsx } from 'clsx';
import { PersonStatus } from '../../types/applicant';

interface TimelineEvent {
  status: PersonStatus;
  label: string;
  timestamp?: string;
  completed: boolean;
}

interface StatusTimelineProps {
  currentStatus: PersonStatus;
  events: TimelineEvent[];
}

const statusOrder: PersonStatus[] = ['active', 'onboarding', 'offboarding', 'archived'];

export function StatusTimeline({ currentStatus, events }: StatusTimelineProps) {
  const currentIndex = statusOrder.indexOf(currentStatus);

  return (
    <div className="relative">
      {/* Timeline line */}
      <div className="absolute top-4 left-0 right-0 h-0.5 bg-zinc-700" />

      <div className="relative flex justify-between">
        {events.map((event, index) => {
          const eventIndex = statusOrder.indexOf(event.status);
          const isCompleted = eventIndex <= currentIndex;
          const isCurrent = event.status === currentStatus;

          return (
            <div key={event.status} className="flex flex-col items-center">
              <div
                className={clsx(
                  'relative z-10 flex items-center justify-center w-8 h-8 rounded-full transition-all duration-300',
                  isCompleted
                    ? 'bg-emerald-500/20 text-emerald-400'
                    : 'bg-zinc-800 text-zinc-500'
                )}
              >
                {isCompleted ? (
                  <CheckCircle2 className="w-5 h-5" />
                ) : isCurrent ? (
                  <Clock className="w-5 h-5 animate-pulse" />
                ) : (
                  <Circle className="w-5 h-5" />
                )}
              </div>
              <div className="mt-3 text-center">
                <p
                  className={clsx(
                    'text-sm font-medium',
                    isCompleted ? 'text-zinc-100' : 'text-zinc-500'
                  )}
                >
                  {event.label}
                </p>
                {event.timestamp && (
                  <p className="text-xs text-zinc-500 mt-0.5">
                    {new Date(event.timestamp).toLocaleDateString('de-DE', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                    })}
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
