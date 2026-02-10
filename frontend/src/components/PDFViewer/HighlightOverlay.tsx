import { motion } from 'framer-motion';
import type { HighlightRegion, PageDimensions } from '../../types/extraction.types';
import { normalizedToPixels, getConfidenceColor } from '../../utils/coordinateMapping';

interface HighlightOverlayProps {
  highlights: HighlightRegion[];
  pageDimensions: PageDimensions | null;
  scale: number;
  onDismiss?: () => void;
}

export function HighlightOverlay({
  highlights,
  pageDimensions,
  scale,
  onDismiss
}: HighlightOverlayProps) {
  if (!pageDimensions || highlights.length === 0) {
    return null;
  }

  return (
    <svg
      className="absolute top-0 left-0 pointer-events-none"
      style={{
        width: pageDimensions.width * scale,
        height: pageDimensions.height * scale,
      }}
      aria-hidden="true"
    >
      {highlights.map((highlight) => {
        if (!highlight.boundingBox) {
          console.warn(`Missing bounding box for field: ${highlight.field}`);
          return null;
        }

        const pixelBox = normalizedToPixels(
          highlight.boundingBox,
          pageDimensions,
          scale
        );

        const isLowConfidence = highlight.confidence < 0.80;
        const strokeDasharray = isLowConfidence ? '6 3' : 'none';
        const fillColor = highlight.isPrimary
          ? 'rgba(255, 235, 59, 0.4)' // Yellow
          : 'rgba(33, 150, 243, 0.25)'; // Blue
        const strokeColor = highlight.isPrimary
          ? 'rgb(255, 193, 7)'
          : getConfidenceColor(highlight.confidence);

        return (
          <motion.g
            key={highlight.id}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            {/* Main highlight box */}
            <rect
              x={pixelBox.x}
              y={pixelBox.y}
              width={pixelBox.width}
              height={pixelBox.height}
              fill={fillColor}
              stroke={strokeColor}
              strokeWidth="2"
              strokeDasharray={strokeDasharray}
              className={highlight.isPrimary ? 'animate-pulse-glow' : ''}
              onClick={onDismiss}
              style={{ cursor: onDismiss ? 'pointer' : 'default' }}
            />

            {/* Confidence indicator (small badge in corner) */}
            {highlight.isPrimary && (
              <>
                <rect
                  x={pixelBox.x + pixelBox.width - 40}
                  y={pixelBox.y - 20}
                  width="40"
                  height="20"
                  fill={getConfidenceColor(highlight.confidence)}
                  rx="4"
                />
                <text
                  x={pixelBox.x + pixelBox.width - 20}
                  y={pixelBox.y - 6}
                  textAnchor="middle"
                  fill="white"
                  fontSize="12"
                  fontWeight="bold"
                >
                  {Math.round(highlight.confidence * 100)}%
                </text>
              </>
            )}
          </motion.g>
        );
      })}
    </svg>
  );
}
