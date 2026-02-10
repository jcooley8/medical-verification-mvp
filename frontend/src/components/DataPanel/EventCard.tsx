import { Search, AlertCircle, CheckCircle } from 'lucide-react';
import type { ChronologyEvent, SourceReference } from '../../types/extraction.types';
import { getConfidenceColor, getConfidenceLabel } from '../../utils/coordinateMapping';

interface EventCardProps {
  event: ChronologyEvent;
  onVerify: (sourceRef: SourceReference) => void;
  isHighlighted: boolean;
}

export function EventCard({ event, onVerify, isHighlighted }: EventCardProps) {
  // Get source refs for different fields
  const dateSourceRef = event.source_refs.find(ref => ref.field === 'date');
  const providerSourceRef = event.source_refs.find(ref => ref.field === 'provider');
  const descriptionSourceRef = event.source_refs.find(ref => ref.field === 'description');

  // Use the first available source ref for the main verify button
  const primarySourceRef = dateSourceRef || providerSourceRef || descriptionSourceRef;

  const getConfidenceBadge = (confidence: number) => {
    if (confidence >= 0.95) return <CheckCircle className="h-4 w-4 text-green-600" />;
    if (confidence >= 0.80) return <CheckCircle className="h-4 w-4 text-blue-600" />;
    return <AlertCircle className="h-4 w-4 text-orange-600" />;
  };

  return (
    <div
      className={`border rounded-lg p-4 transition-all duration-200 group hover:shadow-md ${
        isHighlighted ? 'border-l-4 border-l-yellow-400 bg-yellow-50' : 'hover:bg-gray-50'
      }`}
    >
      {/* Header with date and verify button */}
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-lg font-semibold text-gray-900">
            {event.date}
          </span>
          {dateSourceRef && getConfidenceBadge(dateSourceRef.confidence)}
        </div>
        
        {primarySourceRef && (
          <button
            onClick={() => onVerify(primarySourceRef)}
            className="flex items-center gap-1 px-2 py-1 text-sm rounded-md transition-colors hover:bg-blue-100 text-blue-600"
            title={`Verify source (Page ${primarySourceRef.page_number}, ${getConfidenceLabel(primarySourceRef.confidence)} confidence: ${Math.round(primarySourceRef.confidence * 100)}%)`}
          >
            <Search className="h-4 w-4" />
            <span className="text-xs font-medium">Verify</span>
          </button>
        )}
      </div>

      {/* Provider and facility */}
      <div className="text-sm text-gray-700 mb-1">
        <span className="font-medium">{event.provider}</span>
        {event.facility && (
          <>
            <span className="mx-1 text-gray-400">•</span>
            <span className="text-gray-600">{event.facility}</span>
          </>
        )}
      </div>

      {/* Event type */}
      {event.event_type && (
        <div className="text-xs font-medium text-blue-600 mb-2">
          {event.event_type}
        </div>
      )}

      {/* Description */}
      <p className="text-sm text-gray-600 leading-relaxed">
        {event.description}
      </p>

      {/* Confidence indicators for all fields */}
      {isHighlighted && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="text-xs text-gray-500 space-y-1">
            {dateSourceRef && (
              <div className="flex items-center justify-between">
                <span>Date confidence:</span>
                <span className="font-medium" style={{ color: getConfidenceColor(dateSourceRef.confidence) }}>
                  {Math.round(dateSourceRef.confidence * 100)}%
                </span>
              </div>
            )}
            {providerSourceRef && (
              <div className="flex items-center justify-between">
                <span>Provider confidence:</span>
                <span className="font-medium" style={{ color: getConfidenceColor(providerSourceRef.confidence) }}>
                  {Math.round(providerSourceRef.confidence * 100)}%
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
