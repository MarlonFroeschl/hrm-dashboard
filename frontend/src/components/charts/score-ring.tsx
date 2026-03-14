import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

interface ScoreRingProps {
  score: number | null;
  size?: 'sm' | 'md' | 'lg';
}

const sizeConfig = {
  sm: { outerRadius: 40, innerRadius: 30, fontSize: 'text-sm' },
  md: { outerRadius: 60, innerRadius: 45, fontSize: 'text-xl' },
  lg: { outerRadius: 80, innerRadius: 60, fontSize: 'text-3xl' },
};

const getScoreColor = (score: number): string => {
  if (score >= 80) return '#34d399'; // emerald-400
  if (score >= 60) return '#60a5fa'; // blue-400
  if (score >= 40) return '#fbbf24'; // amber-400
  return '#f87171'; // red-400
};

export function ScoreRing({ score, size = 'md' }: ScoreRingProps) {
  const config = sizeConfig[size];
  const displayScore = score ?? 0;

  const data = [
    { name: 'Score', value: displayScore },
    { name: 'Remaining', value: 100 - displayScore },
  ];

  return (
    <div className="relative flex items-center justify-center">
      <ResponsiveContainer width={config.outerRadius * 2} height={config.outerRadius * 2}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            startAngle={90}
            endAngle={-270}
            innerRadius={config.innerRadius}
            outerRadius={config.outerRadius}
            dataKey="value"
            stroke="none"
          >
            <Cell key="score" fill={getScoreColor(displayScore)} />
            <Cell key="remaining" fill="#3f3f46" />
          </Pie>
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length && payload[0]) {
                return (
                  <div className="bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm">
                    <span className="text-zinc-300">Match Score: </span>
                    <span className="text-zinc-100 font-medium">{String(payload[0].value)}%</span>
                  </div>
                );
              }
              return null;
            }}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="absolute flex flex-col items-center justify-center">
        <span className={`${config.fontSize} font-bold text-zinc-100`}>
          {score !== null ? `${displayScore}%` : 'N/A'}
        </span>
        {size !== 'sm' && <span className="text-xs text-zinc-500">Match</span>}
      </div>
    </div>
  );
}
