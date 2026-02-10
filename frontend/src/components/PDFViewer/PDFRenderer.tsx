import { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut } from 'lucide-react';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

interface PDFRendererProps {
  fileUrl: string;
  currentPage: number;
  onPageChange: (page: number) => void;
  scale: number;
  onScaleChange: (scale: number) => void;
  onPageLoad?: (dimensions: { width: number; height: number }) => void;
  onReady?: () => void;
}

export function PDFRenderer({
  fileUrl,
  currentPage,
  onPageChange,
  scale,
  onScaleChange,
  onPageLoad,
  onReady
}: PDFRendererProps) {
  const [numPages, setNumPages] = useState<number>(0);
  const [loading, setLoading] = useState(true);

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages);
    setLoading(false);
    onReady?.();
  }

  function onPageLoadSuccess(page: any) {
    const viewport = page.getViewport({ scale });
    onPageLoad?.({
      width: viewport.width,
      height: viewport.height,
    });
  }

  const zoomIn = () => onScaleChange(Math.min(scale + 0.25, 2.0));
  const zoomOut = () => onScaleChange(Math.max(scale - 0.25, 0.5));
  const prevPage = () => onPageChange(Math.max(currentPage - 1, 1));
  const nextPage = () => onPageChange(Math.min(currentPage + 1, numPages));

  return (
    <div className="flex flex-col h-full">
      {/* PDF Canvas */}
      <div className="flex-1 overflow-auto bg-gray-100 flex items-center justify-center relative">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
            <div className="text-gray-500">Loading PDF...</div>
          </div>
        )}
        
        <Document
          file={fileUrl}
          onLoadSuccess={onDocumentLoadSuccess}
          onLoadError={(error) => console.error('PDF load error:', error)}
          loading={<div className="text-gray-500">Loading document...</div>}
        >
          <Page
            pageNumber={currentPage}
            scale={scale}
            onLoadSuccess={onPageLoadSuccess}
            renderTextLayer={false}
            renderAnnotationLayer={false}
            className="shadow-lg"
          />
        </Document>
      </div>

      {/* Controls */}
      <div className="border-t bg-white p-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={prevPage}
            disabled={currentPage <= 1}
            className="p-1 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Previous page"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          
          <span className="text-sm font-medium min-w-[120px] text-center">
            Page {currentPage} of {numPages}
          </span>
          
          <button
            onClick={nextPage}
            disabled={currentPage >= numPages}
            className="p-1 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Next page"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={zoomOut}
            disabled={scale <= 0.5}
            className="p-1 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Zoom out"
          >
            <ZoomOut className="h-5 w-5" />
          </button>
          
          <span className="text-sm font-medium min-w-[60px] text-center">
            {Math.round(scale * 100)}%
          </span>
          
          <button
            onClick={zoomIn}
            disabled={scale >= 2.0}
            className="p-1 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Zoom in"
          >
            <ZoomIn className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
