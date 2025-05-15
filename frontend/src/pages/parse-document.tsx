import { useState, useRef, useEffect } from "react";
import { useToast } from "@/hooks/use-toast";
import { Layout } from "@/components/layout";
import { TopBar } from "@/components/top-bar";
import { FileDropzone } from "@/components/file-dropzone";
import { PdfWithOverlay } from "@/components/PdfWithOverlay";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { OcrOverlay, OCRPageResult } from "@/components/OcrOverlay";

export default function ParseDocumentPage() {
  const [pdfPath, setPdfPath] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();
  const [ocrResults, setOcrResults] = useState<OCRPageResult[] | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerSize, setContainerSize] = useState({ width: 0, height: 0 });
  const [isParsing, setIsParsing] = useState(false);

  useEffect(() => {
    if (pdfPath && containerRef.current) {
      const resizeObserver = new ResizeObserver(() => {
        const { offsetWidth, offsetHeight } = containerRef.current!;
        setContainerSize({ width: offsetWidth, height: offsetHeight });
      });
  
      resizeObserver.observe(containerRef.current);
      return () => resizeObserver.disconnect();
    }
  }, [pdfPath]);
  

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleConfigureClick = () => {
    toast({
      title: "Configure Options",
      description:
        "Configuration panel will be implemented in a future version.",
    });
  };

  // const handleFileUpload = async (file: File) => {
  //   setIsUploading(true);
  //   setIsParsing(true);
  //   try {
  //     console.log("Uploading file:", file);
      
  //     if (!file.name.endsWith(".pdf")) {
  //       toast({
  //         title: "Unsupported file type",
  //         description: "Please upload a PDF document.",
  //         variant: "destructive",
  //       });
  //       return;
  //     }

      
  //     //upload file to backend
  //     const formData = new FormData();
  //     formData.append("file", file);

  //     const uploadResponse = await fetch("/api/upload", {
  //       method: "POST",
  //       body: formData,
  //     });

  //     if (!uploadResponse.ok) {
  //       throw new Error("Upload failed");
  //     }

  //     const data = await uploadResponse.json();
  //     setPdfPath(data.path)

  //     // OCR request
  //     const ocrResponse = await fetch("/api/ocr/path", {
  //       method: "POST",
  //       headers: { "Content-Type": "application/json" },
  //       body: JSON.stringify({ path: data.path }),
  //     });
  //     console.log("OCR Response:", ocrResponse);

  //     if (!ocrResponse.ok) {
  //       throw new Error("OCR request failed");
  //     }
      

  //     const ocrData = await ocrResponse.json();
  //     console.log("OCR Response:", ocrData);

  //     setOcrResults(ocrData.pages);
  //     setIsParsing(false);
  //     toast({
  //       title: "File uploaded",
  //       description: `${file.name} uploaded successfully.`,
  //     });
  //   } catch (error) {
  //     toast({
  //       title: "Upload failed",
  //       description: "There was an error uploading your file",
  //       variant: "destructive",
  //     });
  //   } finally {
  //     setIsUploading(false);
  //   }
  // };
  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    setIsParsing(true);
    try {
      // Instead of uploading, just use the static PDF
      setPdfPath('/sample.pdf');
      // Optionally, mock OCR results if needed for overlay
      setOcrResults([
        {
          page: 1,
          results: [],
        },
      ]);
      setIsParsing(false);
      toast({
        title: "File loaded (mocked)",
        description: `${file.name} loaded successfully (mocked).`,
      });
    } catch (error) {
      toast({
        title: "Load failed",
        description: "There was an error loading your file",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Layout>
      <TopBar onUpload={handleUploadClick} onConfigure={handleConfigureClick} />

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.png"
        className="hidden"
        onChange={(e) => {
          const files = e.target.files;
          if (files && files.length > 0) {
            handleFileUpload(files[0]);
          }
        }}
      />

      {!pdfPath ? (
        <div className="mt-8 max-w-4xl mx-auto">
          <FileDropzone onFileUpload={handleFileUpload} />
          {isUploading && (
            <div className="flex justify-center mt-4">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
              <span className="ml-2 text-primary">Uploading...</span>
            </div>
          )}
        </div>
      ) : (
        <div className="mt-8 glass-card h-[80vh] flex flex-col">
          <ResizablePanelGroup
            direction="horizontal"
            className="resizable-panel-container flex-1 h-full"
          >
            <ResizablePanel defaultSize={50} minSize={30} className="flex flex-col h-full">
              <div className="h-full p-4 flex-1 flex flex-col">
                <div ref={containerRef} className="relative w-full h-full flex-1">
                  {pdfPath && ocrResults && (
                    <PdfWithOverlay
                      fileUrl={pdfPath}
                      ocrResults={ocrResults}
                      isLoading={isParsing}
                    />
                  )}
                </div>
              </div>
            </ResizablePanel>

            <ResizableHandle withHandle />

            <ResizablePanel defaultSize={50} minSize={30} className="flex flex-col h-full">
              <div className="h-full p-4 overflow-auto flex-1 flex flex-col">
                <h2 className="text-xl font-semibold mb-4">Extracted Text</h2>
                <div className="rounded-md border p-4 bg-muted/30 min-h-[200px] h-full">
                  <p className="text-muted-foreground text-sm">
                    Document text extraction will appear here.
                  </p>
                </div>
              </div>
            </ResizablePanel>
          </ResizablePanelGroup>
        </div>
      )}
    </Layout>
  );
}
