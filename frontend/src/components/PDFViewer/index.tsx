import { useState, useEffect } from 'react';
import { PDFRenderer } from './PDFRenderer';
import { HighlightOverlay } from './HighlightOverlay';
import type { HighlightRegion, PageDimensions } from '../../types/extraction.types';

interface PDFViewerProps {
  fileUrl: string;
  currentPage: number;
  onPageChange: (page: number) => void;
  highlights: HighlightRegion[];
  onClearHighlight?: () => void;
}

export function PDFViewer({
  fileUrl,
  currentPage,
  onPageChange,
  highlights,
  onClearHighlight
}: PDFViewerProps) {
  const [scale, setScale] = useState(1.0);
  const [pageDimensions, setPageDimensions] = useState<PageDimensions | null>(null);
  const [pdfReady, setPdfReady] = useState(false);

  // Reset page dimensions when page changes
  useEffect(() => {
    setPageDimensions(null);
  }, [currentPage]);

  return (
    <div className="relative h-full border rounded-lg bg-gray-50 overflow-hidden">
      <PDFRenderer
        fileUrl={fileUrl}
        currentPage={currentPage}
        onPageChange={onPageChange}
        scale={scale}
        onScaleChange={setScale}
        onPageLoad={setPageDimensions}
        onReady={() => setPdfReady(true)}
      />
      
      {/* Overlay positioned absolutely on top of PDF */}
      {pdfReady && pageDimensions && (
        <div className="absolute top-0 left-0 right-0 bottom-16 overflow-auto flex items-center justify-center pointer-events-none">
          <HighlightOverlay
            highlights={highlights}
            pageDimensions={pageDimensions}
            scale={scale}
            onDismiss={onClearHighlight}
          />
        </div>
      )}
    </div>
  );
}

export { PDFRenderer } from './PDFRenderer';
export { HighlightOverlay } from './HighlightOverlay';
