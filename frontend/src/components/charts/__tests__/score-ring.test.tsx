import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ScoreRing } from '../score-ring';

describe('ScoreRing', () => {
  it('should render with score value', () => {
    render(<ScoreRing score={85} />);

    expect(screen.getByText('85%')).toBeInTheDocument();
    expect(screen.getByText('Match')).toBeInTheDocument();
  });

  it('should render N/A when score is null', () => {
    render(<ScoreRing score={null} />);

    expect(screen.getByText('N/A')).toBeInTheDocument();
  });


  it('should render small size correctly', () => {
    render(<ScoreRing score={75} size="sm" />);

    expect(screen.getByText('75%')).toBeInTheDocument();
    // Small size should not show "Match" label
    expect(screen.queryByText('Match')).not.toBeInTheDocument();
  });

  it('should render medium size correctly', () => {
    render(<ScoreRing score={60} size="md" />);

    expect(screen.getByText('60%')).toBeInTheDocument();
    expect(screen.getByText('Match')).toBeInTheDocument();
  });

  it('should render large size correctly', () => {
    render(<ScoreRing score={90} size="lg" />);

    expect(screen.getByText('90%')).toBeInTheDocument();
    expect(screen.getByText('Match')).toBeInTheDocument();
  });

  it('should render 0% score correctly', () => {
    render(<ScoreRing score={0} />);

    expect(screen.getByText('0%')).toBeInTheDocument();
  });

  it('should render 100% score correctly', () => {
    render(<ScoreRing score={100} />);

    expect(screen.getByText('100%')).toBeInTheDocument();
  });

  it('should render low score correctly', () => {
    render(<ScoreRing score={25} />);

    expect(screen.getByText('25%')).toBeInTheDocument();
  });

  it('should render medium score correctly', () => {
    render(<ScoreRing score={50} />);

    expect(screen.getByText('50%')).toBeInTheDocument();
  });

  it('should have default medium size', () => {
    render(<ScoreRing score={70} />);

    expect(screen.getByText('70%')).toBeInTheDocument();
    expect(screen.getByText('Match')).toBeInTheDocument();
  });

  it('should render with very low score', () => {
    render(<ScoreRing score={5} />);

    expect(screen.getByText('5%')).toBeInTheDocument();
  });

  it('should render with edge case score 33', () => {
    render(<ScoreRing score={33} />);

    expect(screen.getByText('33%')).toBeInTheDocument();
  });

  it('should render with edge case score 66', () => {
    render(<ScoreRing score={66} />);

    expect(screen.getByText('66%')).toBeInTheDocument();
  });
});
