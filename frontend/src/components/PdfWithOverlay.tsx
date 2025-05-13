import { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { OcrOverlay, OCRPageResult } from '@/components/OcrOverlay';
import useResizeObserver from 'use-resize-observer';


pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

interface PdfWithOverlayProps {
  fileUrl: string;
  ocrResults: OCRPageResult[];
  isLoading?: boolean;
}

export const PdfWithOverlay = ({ fileUrl, ocrResults, isLoading }: PdfWithOverlayProps) => {
  const [pageDims, setPageDims] = useState<{ [page: number]: { height: number } }>({});
  const [numPages, setNumPages] = useState<number>(0);
  const { ref: containerRef, width: containerWidth = 800 } = useResizeObserver<HTMLDivElement>();


  return (
    <div ref={containerRef} className="w-full h-full overflow-auto relative">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-background/80 z-20">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        </div>
      )}
      <Document
        file={fileUrl}
        loading={<p className="text-center">Loading PDF...</p>}
        onLoadSuccess={({ numPages }) => setNumPages(numPages)}
        className="w-full"
      >
        {Array.from({ length: numPages }, (_, i) => {
          const pageNum = i + 1;
          const pageOcr = ocrResults.find((p) => p.page === pageNum);
          return (
            <div key={pageNum} className="relative mb-8 flex justify-center">
              <Page
                pageNumber={pageNum}
                onRenderSuccess={({ height }) =>
                  setPageDims((prev) => ({ ...prev, [pageNum]: { height } }))
                }
                width={containerWidth}
                renderAnnotationLayer={false}
                renderTextLayer={false}
              />
              {pageDims[pageNum] && pageOcr && (
                <div
                  className="absolute top-0 left-0"
                  style={{ width: containerWidth, height: pageDims[pageNum].height }}
                >
                  <OcrOverlay
                    ocrResults={[pageOcr]}
                    containerWidth={containerWidth}
                    containerHeight={pageDims[pageNum].height}
                  />
                </div>
              )}
            </div>
          );
        })}
      </Document>
    </div>
  );
}; 