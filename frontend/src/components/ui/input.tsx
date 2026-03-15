import { forwardRef, InputHTMLAttributes } from 'react';
import { clsx } from 'clsx';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, id, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label htmlFor={id} className="block text-sm font-medium text-zinc-300 mb-1.5">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={id}
          className={clsx(
            'w-full rounded-lg border border-zinc-700 bg-zinc-800/50 px-3 py-2 text-sm text-zinc-100',
            'placeholder:text-zinc-500',
            'focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20',
            'transition-colors duration-200',
            error && 'border-red-500 focus:border-red-500 focus:ring-red-500/20',
            className
          )}
          {...props}
        />
        {error && <p className="mt-1.5 text-sm text-red-400">{error}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';
