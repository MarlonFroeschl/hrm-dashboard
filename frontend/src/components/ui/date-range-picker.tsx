import { Calendar } from 'lucide-react';
import { Input } from './input';

interface DateRangePickerProps {
  label?: string;
  fromDate: string | null;
  toDate: string | null;
  onFromDateChange: (date: string | null) => void;
  onToDateChange: (date: string | null) => void;
}

export function DateRangePicker({
  label,
  fromDate,
  toDate,
  onFromDateChange,
  onToDateChange,
}: DateRangePickerProps) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && <label className="text-sm font-medium text-zinc-300">{label}</label>}
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
          <input
            type="date"
            value={fromDate || ''}
            onChange={(e) => onFromDateChange(e.target.value || null)}
            className="w-full pl-9 pr-3 py-2 rounded-lg border border-zinc-700 bg-zinc-800/50 text-sm text-zinc-100
              focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors"
          />
        </div>
        <span className="text-zinc-500">-</span>
        <div className="relative flex-1">
          <input
            type="date"
            value={toDate || ''}
            onChange={(e) => onToDateChange(e.target.value || null)}
            className="w-full px-3 py-2 rounded-lg border border-zinc-700 bg-zinc-800/50 text-sm text-zinc-100
              focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors"
          />
        </div>
      </div>
    </div>
  );
}
