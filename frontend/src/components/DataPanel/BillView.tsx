import { CreditCard, DollarSign } from 'lucide-react';
import type { BillLineItem, SourceReference } from '../../types/extraction.types';
import { LineItemRow } from './LineItemRow';

interface BillViewProps {
  items: BillLineItem[];
  onVerify: (sourceRef: SourceReference) => void;
  highlightedItemIndex: number | null;
}

export function BillView({
  items,
  onVerify,
  highlightedItemIndex
}: BillViewProps) {
  if (!items || items.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        <CreditCard className="h-12 w-12 mx-auto mb-3 opacity-50" />
        <p className="font-medium">No billing items found</p>
        <p className="text-sm mt-1">Upload a medical bill to extract line items</p>
      </div>
    );
  }

  // Calculate total
  const total = items.reduce((sum, item) => sum + item.total, 0);

  return (
    <div className="space-y-4">
      {/* Header with summary */}
      <div className="px-4 pt-4">
        <h2 className="font-semibold text-lg flex items-center gap-2 mb-3">
          <CreditCard className="h-5 w-5 text-blue-600" />
          Bill Line Items ({items.length})
        </h2>
        
        <div className="flex items-center gap-2 p-3 bg-blue-50 rounded-lg border border-blue-100">
          <DollarSign className="h-5 w-5 text-blue-600" />
          <div>
            <div className="text-sm text-blue-700 font-medium">Total Amount</div>
            <div className="text-2xl font-bold text-blue-900">${total.toFixed(2)}</div>
          </div>
        </div>
      </div>
      
      {/* Line items list */}
      <div className="space-y-3 px-4 pb-4 max-h-[calc(100vh-350px)] overflow-y-auto">
        {items.map((item, index) => (
          <LineItemRow
            key={`${item.cpt_code}-${index}`}
            item={item}
            onVerify={onVerify}
            isHighlighted={index === highlightedItemIndex}
          />
        ))}
      </div>
    </div>
  );
}
