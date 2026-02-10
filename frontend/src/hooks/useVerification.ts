import { useState } from 'react';
import type { SourceReference, HighlightRegion } from '../types/extraction.types';

export function useVerification() {
  const [activeSourceRef, setActiveSourceRef] = useState<SourceReference | null>(null);
  const [highlightRegions, setHighlightRegions] = useState<HighlightRegion[]>([]);

  const verifyField = (sourceRef: SourceReference) => {
    setActiveSourceRef(sourceRef);

    // Convert to highlight region format
    const region: HighlightRegion = {
      id: `${sourceRef.field}-${sourceRef.page_number}`,
      boundingBox: sourceRef.bounding_box,
      field: sourceRef.field,
      confidence: sourceRef.confidence,
      isPrimary: true,
    };

    setHighlightRegions([region]);
  };

  const clearHighlight = () => {
    setActiveSourceRef(null);
    setHighlightRegions([]);
  };

  return {
    activeSourceRef,
    highlightRegions,
    verifyField,
    clearHighlight,
  };
}
