import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Plus,
  Search,
  Filter,
  ChevronDown,
  ChevronUp,
  Trash2,
  Mail,
  MoreHorizontal,
  X,
  RefreshCcw,
} from 'lucide-react';
import { clsx } from 'clsx';
import { Button, Input, Select, Badge, Modal, Slider, DateRangePicker, TableSkeleton } from '../../components/ui';
import { useApplicants, useBulkUpdateStatus } from '../../hooks/use-applicants';
import { useRecruitmentStore, statusColors, getScoreBadgeColor } from '../../stores/recruitment-store';
import { Applicant, PersonStatus } from '../../types/applicant';

type SortField = 'name' | 'score' | 'status' | 'created_at';
type SortDirection = 'asc' | 'desc';

export function ApplicantListPage() {
  const navigate = useNavigate();
  const [showFilters, setShowFilters] = useState(false);
  const [showBulkActions, setShowBulkActions] = useState(false);
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const { filters, setFilters, resetFilters, selectedApplicants, toggleApplicantSelection, clearSelection } =
    useRecruitmentStore();

  const { data, isLoading, error } = useApplicants({
    status: filters.status === 'all' ? undefined : filters.status,
    min_score: filters.scoreRange.min > 0 ? filters.scoreRange.min : undefined,
    max_score: filters.scoreRange.max < 100 ? filters.scoreRange.max : undefined,
    date_from: filters.dateFrom || undefined,
    date_to: filters.dateTo || undefined,
    search: filters.search || undefined,
    page,
    page_size: pageSize,
  });

  const bulkUpdateMutation = useBulkUpdateStatus();

  const applicants = data?.items || [];
  const totalPages = data?.total_pages || 1;

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const sortedApplicants = [...applicants].sort((a, b) => {
    let comparison = 0;
    switch (sortField) {
      case 'name':
        comparison = `${a.last_name} ${a.first_name}`.localeCompare(`${b.last_name} ${b.first_name}`);
        break;
      case 'score':
        comparison = (a.matching_score || 0) - (b.matching_score || 0);
        break;
      case 'status':
        comparison = a.status.localeCompare(b.status);
        break;
      case 'created_at':
        comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
        break;
    }
    return sortDirection === 'asc' ? comparison : -comparison;
  });

  const handleBulkAction = async (action: 'archive' | 'invite') => {
    if (action === 'archive') {
      await bulkUpdateMutation.mutateAsync({
        ids: selectedApplicants,
        status: 'archived',
      });
    }
    clearSelection();
    setShowBulkActions(false);
  };

  const statusOptions = [
    { value: 'all', label: 'Alle Status' },
    { value: 'active', label: 'Aktiv' },
    { value: 'onboarding', label: 'Onboarding' },
    { value: 'offboarding', label: 'Offboarding' },
    { value: 'archived', label: 'Archiviert' },
  ];

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-zinc-100">Bewerber</h1>
            <p className="text-sm text-zinc-500 mt-1">
              {data?.total || 0} Bewerber gefunden
            </p>
          </div>
          <div className="flex items-center gap-3">
            {selectedApplicants.length > 0 && (
              <div className="flex items-center gap-2 mr-4">
                <span className="text-sm text-zinc-400">{selectedApplicants.length} ausgewählt</span>
                <Button variant="ghost" size="sm" onClick={clearSelection}>
                  <X className="w-4 h-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowBulkActions(!showBulkActions)}
                >
                  <MoreHorizontal className="w-4 h-4" />
                </Button>
              </div>
            )}
            <Button onClick={() => navigate('/recruiting/new')}>
              <Plus className="w-4 h-4" />
              Neuer Bewerber
            </Button>
          </div>
        </div>

        {/* Bulk Actions */}
        {showBulkActions && selectedApplicants.length > 0 && (
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 flex items-center justify-between animate-in slide-in-from-top-2">
            <p className="text-sm text-zinc-300">Massenaktion für {selectedApplicants.length} Bewerber</p>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={() => handleBulkAction('invite')}>
                <Mail className="w-4 h-4" />
                Einladen
              </Button>
              <Button variant="outline" size="sm" onClick={() => handleBulkAction('archive')}>
                <Trash2 className="w-4 h-4" />
                Archivieren
              </Button>
            </div>
          </div>
        )}

        {/* Search & Filters */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-4">
          <div className="flex items-center gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
              <input
                type="text"
                placeholder="Bewerber suchen..."
                value={filters.search}
                maxLength={100}
                onChange={(e) => {
                  // Input sanitization: max length + strip dangerous characters
                  const sanitized = e.target.value.slice(0, 100).replace(/[<>]/g, '');
                  setFilters({ search: sanitized });
                }}
                className="w-full pl-10 pr-4 py-2 rounded-lg bg-zinc-800/50 border border-zinc-700 text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              />
            </div>
            <Select
              value={filters.status}
              onChange={(e) => setFilters({ status: e.target.value as PersonStatus | 'all' })}
              options={statusOptions}
              className="w-40"
            />
            <Button
              variant={showFilters ? 'secondary' : 'outline'}
              onClick={() => setShowFilters(!showFilters)}
            >
              <Filter className="w-4 h-4" />
              Filter
            </Button>
            {(filters.scoreRange.min > 0 ||
              filters.scoreRange.max < 100 ||
              filters.dateFrom ||
              filters.dateTo) && (
              <Button variant="ghost" size="sm" onClick={resetFilters}>
                <RefreshCcw className="w-4 h-4" />
                Zurücksetzen
              </Button>
            )}
          </div>

          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4 border-t border-zinc-800">
              <Slider
                label="Score-Range"
                min={0}
                max={100}
                value={[filters.scoreRange.min, filters.scoreRange.max]}
                onChange={([min, max]) => setFilters({ scoreRange: { min, max } })}
              />
              <DateRangePicker
                label="Bewerbungsdatum"
                fromDate={filters.dateFrom}
                toDate={filters.dateTo}
                onFromDateChange={(date) => setFilters({ dateFrom: date })}
                onToDateChange={(date) => setFilters({ dateTo: date })}
              />
            </div>
          )}
        </div>

        {/* Table */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-zinc-800 bg-zinc-800/30">
                  <th className="w-10 px-4 py-3">
                    <input
                      type="checkbox"
                      checked={selectedApplicants.length === applicants.length && applicants.length > 0}
                      onChange={() => {
                        if (selectedApplicants.length === applicants.length) {
                          clearSelection();
                        } else {
                          applicants.forEach((a) => toggleApplicantSelection(a.id));
                        }
                      }}
                      className="rounded border-zinc-600 bg-zinc-800 text-blue-600"
                    />
                  </th>
                  <th
                    className="px-4 py-3 text-left text-xs font-medium text-zinc-400 uppercase tracking-wider cursor-pointer hover:text-zinc-200"
                    onClick={() => handleSort('name')}
                  >
                    <div className="flex items-center gap-1">
                      Name
                      {sortField === 'name' && (sortDirection === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />)}
                    </div>
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-zinc-400 uppercase tracking-wider">
                    Rolle
                  </th>
                  <th
                    className="px-4 py-3 text-left text-xs font-medium text-zinc-400 uppercase tracking-wider cursor-pointer hover:text-zinc-200"
                    onClick={() => handleSort('score')}
                  >
                    <div className="flex items-center gap-1">
                      Score
                      {sortField === 'score' && (sortDirection === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />)}
                    </div>
                  </th>
                  <th
                    className="px-4 py-3 text-left text-xs font-medium text-zinc-400 uppercase tracking-wider cursor-pointer hover:text-zinc-200"
                    onClick={() => handleSort('status')}
                  >
                    <div className="flex items-center gap-1">
                      Status
                      {sortField === 'status' && (sortDirection === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />)}
                    </div>
                  </th>
                  <th
                    className="px-4 py-3 text-left text-xs font-medium text-zinc-400 uppercase tracking-wider cursor-pointer hover:text-zinc-200"
                    onClick={() => handleSort('created_at')}
                  >
                    <div className="flex items-center gap-1">
                      Datum
                      {sortField === 'created_at' && (sortDirection === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />)}
                    </div>
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-zinc-400 uppercase tracking-wider">
                    Aktionen
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800">
                {isLoading ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-8">
                      <TableSkeleton rows={5} />
                    </td>
                  </tr>
                ) : error ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center text-red-400">
                      Fehler beim Laden der Bewerber
                    </td>
                  </tr>
                ) : sortedApplicants.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center text-zinc-500">
                      Keine Bewerber gefunden
                    </td>
                  </tr>
                ) : (
                  sortedApplicants.map((applicant) => (
                    <tr
                      key={applicant.id}
                      className="hover:bg-zinc-800/30 transition-colors cursor-pointer"
                      onClick={() => navigate(`/recruiting/${applicant.id}`)}
                    >
                      <td className="px-4 py-4" onClick={(e) => e.stopPropagation()}>
                        <input
                          type="checkbox"
                          checked={selectedApplicants.includes(applicant.id)}
                          onChange={() => toggleApplicantSelection(applicant.id)}
                          className="rounded border-zinc-600 bg-zinc-800 text-blue-600"
                        />
                      </td>
                      <td className="px-4 py-4">
                        <div>
                          <p className="font-medium text-zinc-100">
                            {applicant.first_name} {applicant.last_name}
                          </p>
                          <p className="text-sm text-zinc-500">{applicant.email}</p>
                        </div>
                      </td>
                      <td className="px-4 py-4 text-zinc-300">
                        {applicant.extracted_data?.summary?.slice(0, 30) || '-'}
                      </td>
                      <td className="px-4 py-4">
                        <span className={clsx('px-2.5 py-1 rounded-full text-xs font-medium', getScoreBadgeColor(applicant.matching_score))}>
                          {applicant.matching_score !== null ? `${applicant.matching_score}%` : 'N/A'}
                        </span>
                      </td>
                      <td className="px-4 py-4">
                        <span
                          className={clsx(
                            'px-2.5 py-1 rounded-full text-xs font-medium',
                            statusColors[applicant.status].bg,
                            statusColors[applicant.status].text
                          )}
                        >
                          {statusColors[applicant.status].label}
                        </span>
                      </td>
                      <td className="px-4 py-4 text-zinc-400 text-sm">
                        {new Date(applicant.created_at).toLocaleDateString('de-DE', {
                          day: '2-digit',
                          month: '2-digit',
                          year: 'numeric',
                        })}
                      </td>
                      <td className="px-4 py-4 text-right" onClick={(e) => e.stopPropagation()}>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => navigate(`/recruiting/${applicant.id}`)}
                        >
                          Ansehen
                        </Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-4 py-3 border-t border-zinc-800">
              <p className="text-sm text-zinc-500">
                Seite {page} von {totalPages}
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page === 1}
                  onClick={() => setPage(page - 1)}
                >
                  Zurück
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page === totalPages}
                  onClick={() => setPage(page + 1)}
                >
                  Weiter
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
