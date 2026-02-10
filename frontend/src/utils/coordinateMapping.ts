import type { BoundingBox, PixelBox, PageDimensions } from '../types/extraction.types';

/**
 * Convert normalized coordinates (0-1) to pixel coordinates
 */
export function normalizedToPixels(
  bbox: BoundingBox,
  pageDimensions: PageDimensions,
  scale: number = 1
): PixelBox {
  return {
    x: bbox.left * pageDimensions.width * scale,
    y: bbox.top * pageDimensions.height * scale,
    width: bbox.width * pageDimensions.width * scale,
    height: bbox.height * pageDimensions.height * scale,
  };
}

/**
 * Validate bounding box coordinates are within 0-1 range
 */
export function validateBoundingBox(bbox: BoundingBox): boolean {
  return (
    bbox.left >= 0 && bbox.left <= 1 &&
    bbox.top >= 0 && bbox.top <= 1 &&
    bbox.width >= 0 && bbox.width <= 1 &&
    bbox.height >= 0 && bbox.height <= 1 &&
    bbox.left + bbox.width <= 1 &&
    bbox.top + bbox.height <= 1
  );
}

/**
 * Get confidence color based on threshold
 */
export function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.95) return 'rgb(76, 175, 80)'; // Green
  if (confidence >= 0.80) return 'rgb(33, 150, 243)'; // Blue
  if (confidence >= 0.60) return 'rgb(255, 152, 0)'; // Orange
  return 'rgb(244, 67, 54)'; // Red
}

/**
 * Get confidence label
 */
export function getConfidenceLabel(confidence: number): string {
  if (confidence >= 0.95) return 'High';
  if (confidence >= 0.80) return 'Good';
  if (confidence >= 0.60) return 'Medium';
  return 'Low';
}
