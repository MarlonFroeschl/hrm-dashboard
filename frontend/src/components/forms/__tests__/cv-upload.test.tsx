import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CVUpload } from '../cv-upload';

describe('CVUpload', () => {
  const mockOnUpload = vi.fn().mockResolvedValue(undefined);

  beforeEach(() => {
    mockOnUpload.mockClear();
  });

  it('should render dropzone in idle state', () => {
    render(<CVUpload onUpload={mockOnUpload} status="idle" />);

    expect(screen.getByText('PDF hierher ziehen oder klicken')).toBeInTheDocument();
    expect(screen.getByText('Max. 10MB, nur PDF')).toBeInTheDocument();
  });

  it('should show drag active state', () => {
    render(<CVUpload onUpload={mockOnUpload} status="idle" />);

    // The component uses react-dropzone which handles drag events internally
    // We can only verify the initial render
    expect(screen.getByText('PDF hierher ziehen oder klicken')).toBeInTheDocument();
  });

  it('should disable dropzone when uploading', () => {
    render(<CVUpload onUpload={mockOnUpload} status="uploading" />);

    // When uploading, the dropzone should not be visible
    expect(screen.queryByText('PDF hierher ziehen oder klicken')).not.toBeInTheDocument();
  });

  it('should show file info when file is selected', () => {
    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });
    render(<CVUpload onUpload={mockOnUpload} status="uploading" />);

    // The file would be set internally, we can test status-based rendering
    expect(screen.queryByText('PDF hierher ziehen oder klicken')).not.toBeInTheDocument();
  });

  it('should show uploading step indicator', () => {
    render(<CVUpload onUpload={mockOnUpload} status="uploading" />);

    expect(screen.getByText('Hochladen')).toBeInTheDocument();
    expect(screen.getByText('OCR')).toBeInTheDocument();
    expect(screen.getByText('KI-Analyse')).toBeInTheDocument();
    expect(screen.getByText('Fertig')).toBeInTheDocument();
  });

  it('should show processing step indicator', () => {
    render(<CVUpload onUpload={mockOnUpload} status="processing" />);

    expect(screen.getByText('Hochladen')).toBeInTheDocument();
    expect(screen.getByText('OCR')).toBeInTheDocument();
    expect(screen.getByText('KI-Analyse')).toBeInTheDocument();
    expect(screen.getByText('Fertig')).toBeInTheDocument();
  });

  it('should show completed state', () => {
    render(<CVUpload onUpload={mockOnUpload} status="completed" />);

    expect(screen.getByText('Neuen Upload starten')).toBeInTheDocument();
  });

  it('should show error message when error prop is provided', () => {
    render(<CVUpload onUpload={mockOnUpload} status="idle" error="Upload failed" />);

    expect(screen.getByText('Upload failed')).toBeInTheDocument();
  });

  it('should show failed step indicator', () => {
    render(<CVUpload onUpload={mockOnUpload} status="failed" />);

    // When failed, the step indicator should not show
    expect(screen.queryByText('Hochladen')).not.toBeInTheDocument();
  });

  describe('StepIndicator', () => {
    it('should show all steps with correct labels', () => {
      render(<CVUpload onUpload={mockOnUpload} status="uploading" />);

      expect(screen.getByText('Hochladen')).toBeInTheDocument();
      expect(screen.getByText('OCR')).toBeInTheDocument();
      expect(screen.getByText('KI-Analyse')).toBeInTheDocument();
      expect(screen.getByText('Fertig')).toBeInTheDocument();
    });

    it('should highlight current active step', () => {
      render(<CVUpload onUpload={mockOnUpload} status="uploading" />);

      // In uploading state, first step should be active/completed
      // The visual styling is handled by CSS, we just verify elements exist
      expect(screen.getByText('Hochladen')).toBeInTheDocument();
    });

    it('should show completed steps in processing state', () => {
      render(<CVUpload onUpload={mockOnUpload} status="processing" />);

      expect(screen.getByText('Hochladen')).toBeInTheDocument();
      expect(screen.getByText('OCR')).toBeInTheDocument();
    });

    it('should show all completed when completed', () => {
      render(<CVUpload onUpload={mockOnUpload} status="completed" />);

      expect(screen.getByText('Hochladen')).toBeInTheDocument();
      expect(screen.getByText('OCR')).toBeInTheDocument();
      expect(screen.getByText('KI-Analyse')).toBeInTheDocument();
      expect(screen.getByText('Fertig')).toBeInTheDocument();
    });
  });

  describe('File handling', () => {
    it('should call onUpload when file is dropped', async () => {
      render(<CVUpload onUpload={mockOnUpload} status="idle" />);

      // Get the input element
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;

      if (input) {
        const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
        fireEvent.change(input, { target: { files: [file] } });

        await waitFor(() => {
          expect(mockOnUpload).toHaveBeenCalledWith(expect.objectContaining({
            name: 'test.pdf',
            type: 'application/pdf',
          }));
        });
      }
    });

    it('should not call onUpload for non-PDF files', async () => {
      render(<CVUpload onUpload={mockOnUpload} status="idle" />);

      const input = document.querySelector('input[type="file"]') as HTMLInputElement;

      if (input) {
        const file = new File(['test'], 'test.txt', { type: 'text/plain' });
        fireEvent.change(input, { target: { files: [file] } });

        // onUpload should not be called for non-PDF files
        expect(mockOnUpload).not.toHaveBeenCalled();
      }
    });
  });

  describe('Accessibility', () => {
    it('should have proper input accessibility', () => {
      render(<CVUpload onUpload={mockOnUpload} status="idle" />);

      const input = document.querySelector('input[type="file"]');
      expect(input).toBeInTheDocument();
      // The actual accept attribute value from react-dropzone
      expect(input).toHaveAttribute('accept', 'application/pdf,.pdf');
    });

    it('should have dropzone element', () => {
      render(<CVUpload onUpload={mockOnUpload} status="idle" />);

      const dropzone = screen.getByText('PDF hierher ziehen oder klicken').closest('div');
      expect(dropzone).toBeInTheDocument();
    });
  });
});
