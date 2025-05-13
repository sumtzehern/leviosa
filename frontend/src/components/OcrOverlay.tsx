import React from "react";

export interface OcrLine {
  line_id: string;
  text: string;
  bbox_norm: [number, number, number, number]; // [x1, y1, x2, y2] normalized
  confidence: number;
  low_confidence?: boolean;
}

export interface OCRPageResult {
  page: number;
  results: OcrLine[];
}

interface OcrOverlayProps {
  ocrResults: OCRPageResult[];
  containerWidth: number;
  containerHeight: number;
}

export const OcrOverlay: React.FC<OcrOverlayProps> = ({
  ocrResults,
  containerWidth,
  containerHeight,
}) => {
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        top: 0,
        width: containerWidth,
        height: containerHeight,
        pointerEvents: "none",
      }}
    >
      {ocrResults.flatMap((page) =>
        page.results.map((line) => {
          const [x1, y1, x2, y2] = line.bbox_norm;
          const left = x1 * containerWidth;
          const top = y1 * containerHeight;
          const width = (x2 - x1) * containerWidth;
          const height = (y2 - y1) * containerHeight;
          const isLow = line.low_confidence ?? line.confidence < 0.6;

          return (
            <div
              key={line.line_id}
              style={{
                position: "absolute",
                left,
                top,
                width,
                height,
                border: isLow ? "2px dashed orange" : "2px solid green",
                backgroundColor: isLow
                  ? "rgba(255, 165, 0, 0.08)"
                  : "rgba(0, 255, 0, 0.05)",
                color: "#333",
                fontSize: 10,
                overflow: "hidden",
                pointerEvents: "auto",
                zIndex: 10,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
              }}
              title={`${line.text} (${Math.round(line.confidence * 100)}%)`}
            >
              <span className="opacity-60 text-xs text-black">
                {line.text}
              </span>
            </div>
          );
        })
      )}
    </div>
  );
};
