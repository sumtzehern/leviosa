
import { useState, useEffect } from 'react';

interface PdfViewerProps {
  src: string | null;
}

export function PdfViewer({ src }: PdfViewerProps) {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (src) {
      setLoading(true);
      const timer = setTimeout(() => {
        setLoading(false);
      }, 1000);
      
      return () => clearTimeout(timer);
    }
  }, [src]);

  if (!src) {
    return (
      <div className="pdf-container flex justify-center items-center bg-muted/50">
        <p className="text-muted-foreground">No document loaded</p>
      </div>
    );
  }

  return (
    <div className="pdf-container relative">
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-background/80">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        </div>
      )}
      
      <iframe 
        src={src} 
        className="w-full h-full"
        title="PDF Viewer"
      />
    </div>
  );
}
