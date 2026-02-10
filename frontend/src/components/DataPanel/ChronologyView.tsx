import { Activity } from 'lucide-react';
import type { ChronologyEvent, SourceReference } from '../../types/extraction.types';
import { EventCard } from './EventCard';

interface ChronologyViewProps {
  events: ChronologyEvent[];
  onVerify: (sourceRef: SourceReference) => void;
  highlightedEventIndex: number | null;
}

export function ChronologyView({
  events,
  onVerify,
  highlightedEventIndex
}: ChronologyViewProps) {
  if (!events || events.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        <Activity className="h-12 w-12 mx-auto mb-3 opacity-50" />
        <p className="font-medium">No chronology events found</p>
        <p className="text-sm mt-1">Upload a medical record to extract events</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h2 className="font-semibold text-lg flex items-center gap-2 px-4 pt-4">
        <Activity className="h-5 w-5 text-blue-600" />
        Medical Events ({events.length})
      </h2>
      
      <div className="space-y-3 px-4 pb-4 max-h-[calc(100vh-250px)] overflow-y-auto">
        {events.map((event, index) => (
          <EventCard
            key={`${event.date}-${index}`}
            event={event}
            onVerify={onVerify}
            isHighlighted={index === highlightedEventIndex}
          />
        ))}
      </div>
    </div>
  );
}
