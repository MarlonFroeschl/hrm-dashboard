import { clsx } from 'clsx';

interface SliderProps {
  label?: string;
  min: number;
  max: number;
  value: [number, number];
  onChange: (value: [number, number]) => void;
  step?: number;
}

export function Slider({ label, min, max, value, onChange, step = 5 }: SliderProps) {
  const percentage1 = ((value[0] - min) / (max - min)) * 100;
  const percentage2 = ((value[1] - min) / (max - min)) * 100;

  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between items-center mb-2">
          <label className="text-sm font-medium text-zinc-300">{label}</label>
          <span className="text-xs text-zinc-500">
            {value[0]}% - {value[1]}%
          </span>
        </div>
      )}
      <div className="relative h-2">
        {/* Track background */}
        <div className="absolute inset-0 bg-zinc-700 rounded-full" />
        {/* Active range */}
        <div
          className="absolute h-full bg-blue-600 rounded-full"
          style={{
            left: `${percentage1}%`,
            width: `${percentage2 - percentage1}%`,
          }}
        />
        {/* Input sliders */}
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value[0]}
          onChange={(e) => {
            const newValue = Math.min(Number(e.target.value), value[1] - step);
            onChange([newValue, value[1]]);
          }}
          className="absolute inset-0 w-full appearance-none bg-transparent cursor-pointer
            [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4
            [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full
            [&::-webkit-slider-thumb]:bg-blue-500 [&::-webkit-slider-thumb]:shadow-lg
            [&::-webkit-slider-thumb]:cursor-grab [&::-webkit-slider-thumb]:transition-transform
            hover:[&::-webkit-slider-thumb]:scale-110"
        />
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value[1]}
          onChange={(e) => {
            const newValue = Math.max(Number(e.target.value), value[0] + step);
            onChange([value[0], newValue]);
          }}
          className="absolute inset-0 w-full appearance-none bg-transparent cursor-pointer
            [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4
            [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full
            [&::-webkit-slider-thumb]:bg-blue-500 [&::-webkit-slider-thumb]:shadow-lg
            [&::-webkit-slider-thumb]:cursor-grab [&::-webkit-slider-thumb]:transition-transform
            hover:[&::-webkit-slider-thumb]:scale-110"
        />
      </div>
    </div>
  );
}
