import { Search, AlertCircle, CheckCircle } from 'lucide-react';
import type { BillLineItem, SourceReference } from '../../types/extraction.types';
import { getConfidenceColor, getConfidenceLabel } from '../../utils/coordinateMapping';

interface LineItemRowProps {
  item: BillLineItem;
  onVerify: (sourceRef: SourceReference) => void;
  isHighlighted: boolean;
}

export function LineItemRow({ item, onVerify, isHighlighted }: LineItemRowProps) {
  // Get source refs for different fields
  const cptSourceRef = item.source_refs.find(ref => ref.field === 'cpt_code');
  const priceSourceRef = item.source_refs.find(ref => ref.field === 'unit_price' || ref.field === 'total');
  
  // Use the first available source ref for the main verify button
  const primarySourceRef = cptSourceRef || priceSourceRef || item.source_refs[0];

  const getConfidenceBadge = (confidence: number) => {
    if (confidence >= 0.95) return <CheckCircle className="h-4 w-4 text-green-600" />;
    if (confidence >= 0.80) return <CheckCircle className="h-4 w-4 text-blue-600" />;
    return <AlertCircle className="h-4 w-4 text-orange-600" />;
  };

  return (
    <div
      className={`border rounded-lg p-4 transition-all duration-200 hover:shadow-md ${
        isHighlighted ? 'border-l-4 border-l-yellow-400 bg-yellow-50' : 'hover:bg-gray-50'
      }`}
    >
      <div className="flex items-start justify-between">
        {/* Left side: CPT code and description */}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg font-bold text-gray-900">
              {item.cpt_code}
            </span>
            {cptSourceRef && getConfidenceBadge(cptSourceRef.confidence)}
          </div>
          
          <p className="text-sm text-gray-600 mb-2">
            {item.description}
          </p>
          
          <div className="flex items-center gap-4 text-xs text-gray-500">
            <span>Date: {item.date_of_service}</span>
            <span>Qty: {item.quantity}</span>
            <span>Unit: ${item.unit_price.toFixed(2)}</span>
          </div>
        </div>

        {/* Right side: Total and verify button */}
        <div className="flex flex-col items-end gap-2 ml-4">
          <div className="flex items-center gap-2">
            <span className="text-xl font-bold text-gray-900">
              ${item.total.toFixed(2)}
            </span>
            {priceSourceRef && getConfidenceBadge(priceSourceRef.confidence)}
          </div>
          
          {primarySourceRef && (
            <button
              onClick={() => onVerify(primarySourceRef)}
              className="flex items-center gap-1 px-3 py-1.5 text-sm rounded-md transition-colors hover:bg-blue-100 text-blue-600 font-medium"
              title={`Verify source (Page ${primarySourceRef.page_number}, ${getConfidenceLabel(primarySourceRef.confidence)} confidence: ${Math.round(primarySourceRef.confidence * 100)}%)`}
            >
              <Search className="h-4 w-4" />
              Verify
            </button>
          )}
        </div>
      </div>

      {/* Confidence details when highlighted */}
      {isHighlighted && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="text-xs text-gray-500 space-y-1">
            {cptSourceRef && (
              <div className="flex items-center justify-between">
                <span>CPT Code confidence:</span>
                <span className="font-medium" style={{ color: getConfidenceColor(cptSourceRef.confidence) }}>
                  {Math.round(cptSourceRef.confidence * 100)}%
                </span>
              </div>
            )}
            {priceSourceRef && (
              <div className="flex items-center justify-between">
                <span>Price confidence:</span>
                <span className="font-medium" style={{ color: getConfidenceColor(priceSourceRef.confidence) }}>
                  {Math.round(priceSourceRef.confidence * 100)}%
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
