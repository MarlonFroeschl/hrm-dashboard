import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface BadgeProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info' | 'secondary';
}

export function Badge({ children, className, variant = 'default' }: BadgeProps) {
  const variants = {
    default: 'bg-gray-500/20 text-gray-300',
    success: 'bg-emerald-500/20 text-emerald-400',
    warning: 'bg-amber-500/20 text-amber-400',
    error: 'bg-red-500/20 text-red-400',
    info: 'bg-blue-500/20 text-blue-400',
    secondary: 'bg-zinc-700/50 text-zinc-300',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
