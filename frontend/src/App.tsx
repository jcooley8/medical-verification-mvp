import { useState, useEffect } from 'react';
import { Activity } from 'lucide-react';
import { cn } from '@/lib/utils';
import { PDFViewer } from './components/PDFViewer';
import { ChronologyView, BillView } from './components/DataPanel';
import { useVerification } from './hooks/useVerification';
import { mockExtractionData } from './data/mockData';
import type { SourceReference } from './types/extraction.types';

function App() {
  const [activeTab, setActiveTab] = useState<'chronology' | 'billing'>('chronology');
  const [currentPage, setCurrentPage] = useState(1);
  const [highlightedEventIndex, setHighlightedEventIndex] = useState<number | null>(null);
  const [highlightedBillIndex, setHighlightedBillIndex] = useState<number | null>(null);
  
  const { highlightRegions, verifyField, clearHighlight } = useVerification();

  // Handle verification from chronology or bill data
  const handleVerify = (sourceRef: SourceReference, itemIndex: number) => {
    // Clear previous highlights
    clearHighlight();
    
    // Navigate to the page containing the source
    setCurrentPage(sourceRef.page_number);
    
    // Set up the highlight
    verifyField(sourceRef);
    
    // Track which item is highlighted
    if (activeTab === 'chronology') {
      setHighlightedEventIndex(itemIndex);
      setHighlightedBillIndex(null);
    } else {
      setHighlightedBillIndex(itemIndex);
      setHighlightedEventIndex(null);
    }
  };

  const handleClearHighlight = () => {
    clearHighlight();
    setHighlightedEventIndex(null);
    setHighlightedBillIndex(null);
  };

  // Clear highlights when switching tabs
  useEffect(() => {
    handleClearHighlight();
  }, [activeTab]);

  // For now, use a placeholder PDF URL
  // In production, this would come from the extraction result
  const pdfUrl = mockExtractionData.pdf_url || '';

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 flex flex-col">
      {/* Header */}
      <header className="border-b bg-white p-4 flex items-center gap-3 shadow-sm">
        <Activity className="h-6 w-6 text-blue-600" />
        <h1 className="text-xl font-bold">Medical Verification MVP - Click-to-Verify</h1>
        <div className="ml-auto text-sm text-gray-500">
          Document: {mockExtractionData.document_id}
        </div>
      </header>

      <main className="flex-1 p-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: PDF Viewer */}
        <div className="h-[calc(100vh-120px)]">
          {pdfUrl ? (
            <PDFViewer
              fileUrl={pdfUrl}
              currentPage={currentPage}
              onPageChange={setCurrentPage}
              highlights={highlightRegions}
              onClearHighlight={handleClearHighlight}
            />
          ) : (
            <div className="border rounded-lg bg-white p-8 h-full flex items-center justify-center">
              <div className="text-center text-gray-500">
                <Activity className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p className="font-medium">No PDF available</p>
                <p className="text-sm mt-1">Upload a document to view PDF</p>
              </div>
            </div>
          )}
        </div>

        {/* Right: Data Panel */}
        <div className="border rounded-lg shadow-sm bg-white h-[calc(100vh-120px)] overflow-hidden flex flex-col">
          {/* Tab Switcher */}
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('chronology')}
              className={cn(
                'flex-1 p-3 text-sm font-medium transition-colors',
                activeTab === 'chronology'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-600 hover:bg-gray-50'
              )}
            >
              Medical Chronology
              {mockExtractionData.chronology && (
                <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
                  {mockExtractionData.chronology.length}
                </span>
              )}
            </button>
            <button
              onClick={() => setActiveTab('billing')}
              className={cn(
                'flex-1 p-3 text-sm font-medium transition-colors',
                activeTab === 'billing'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-600 hover:bg-gray-50'
              )}
            >
              Billing
              {mockExtractionData.bills && (
                <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
                  {mockExtractionData.bills.length}
                </span>
              )}
            </button>
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-hidden">
            {activeTab === 'chronology' ? (
              <ChronologyView
                events={mockExtractionData.chronology || []}
                onVerify={(sourceRef) => {
                  const index = mockExtractionData.chronology?.findIndex(
                    (e) => e.source_refs.some((ref) => ref === sourceRef)
                  );
                  handleVerify(sourceRef, index ?? -1);
                }}
                highlightedEventIndex={highlightedEventIndex}
              />
            ) : (
              <BillView
                items={mockExtractionData.bills || []}
                onVerify={(sourceRef) => {
                  const index = mockExtractionData.bills?.findIndex(
                    (b) => b.source_refs.some((ref) => ref === sourceRef)
                  );
                  handleVerify(sourceRef, index ?? -1);
                }}
                highlightedItemIndex={highlightedBillIndex}
              />
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
