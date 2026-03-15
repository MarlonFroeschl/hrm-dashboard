import { clsx } from 'clsx';

interface Skill {
  name: string;
  matched?: boolean;
}

interface SkillsCloudProps {
  skills: Skill[];
  title?: string;
}

export function SkillsCloud({ skills, title }: SkillsCloudProps) {
  const matchedSkills = skills.filter((s) => s.matched);
  const unmatchedSkills = skills.filter((s) => !s.matched);

  return (
    <div className="space-y-4">
      {title && <h3 className="text-sm font-medium text-zinc-300">{title}</h3>}

      {matchedSkills.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs text-emerald-400 font-medium">Match</p>
          <div className="flex flex-wrap gap-2">
            {matchedSkills.map((skill, index) => (
              <span
                key={`match-${index}`}
                className={clsx(
                  'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium',
                  'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                )}
              >
                {skill.name}
              </span>
            ))}
          </div>
        </div>
      )}

      {unmatchedSkills.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs text-zinc-500 font-medium">Kein Match</p>
          <div className="flex flex-wrap gap-2">
            {unmatchedSkills.map((skill, index) => (
              <span
                key={`unmatch-${index}`}
                className={clsx(
                  'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium',
                  'bg-zinc-800 text-zinc-400 border border-zinc-700'
                )}
              >
                {skill.name}
              </span>
            ))}
          </div>
        </div>
      )}

      {skills.length === 0 && (
        <p className="text-sm text-zinc-500 italic">Keine Skills verfügbar</p>
      )}
    </div>
  );
}
