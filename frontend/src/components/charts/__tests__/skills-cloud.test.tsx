import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SkillsCloud } from '../skills-cloud';

describe('SkillsCloud', () => {
  const mockSkills = [
    { name: 'TypeScript', matched: true },
    { name: 'React', matched: true },
    { name: 'Kommunikation', matched: false },
    { name: 'Teamwork', matched: false },
    { name: 'Python', matched: true },
  ];

  it('should render matched skills', () => {
    render(<SkillsCloud skills={mockSkills} />);

    expect(screen.getByText('TypeScript')).toBeInTheDocument();
    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByText('Python')).toBeInTheDocument();
  });

  it('should render unmatched skills', () => {
    render(<SkillsCloud skills={mockSkills} />);

    expect(screen.getByText('Kommunikation')).toBeInTheDocument();
    expect(screen.getByText('Teamwork')).toBeInTheDocument();
  });

  it('should render empty array without errors', () => {
    render(<SkillsCloud skills={[]} />);

    expect(document.body).toBeInTheDocument();
  });

  it('should render skills with different matched states', () => {
    render(<SkillsCloud skills={mockSkills} />);

    // All skills should be present
    expect(screen.getByText('TypeScript')).toBeInTheDocument();
    expect(screen.getByText('Kommunikation')).toBeInTheDocument();
  });

  it('should handle single skill', () => {
    render(<SkillsCloud skills={[{ name: 'Node.js', matched: true }]} />);

    expect(screen.getByText('Node.js')).toBeInTheDocument();
  });

  it('should handle all matched skills', () => {
    const allMatched = [
      { name: 'Skill1', matched: true },
      { name: 'Skill2', matched: true },
    ];

    render(<SkillsCloud skills={allMatched} />);

    expect(screen.getByText('Skill1')).toBeInTheDocument();
    expect(screen.getByText('Skill2')).toBeInTheDocument();
  });

  it('should handle all unmatched skills', () => {
    const allUnmatched = [
      { name: 'Soft1', matched: false },
      { name: 'Soft2', matched: false },
    ];

    render(<SkillsCloud skills={allUnmatched} />);

    expect(screen.getByText('Soft1')).toBeInTheDocument();
    expect(screen.getByText('Soft2')).toBeInTheDocument();
  });
});
