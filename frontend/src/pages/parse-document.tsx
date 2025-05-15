import { useState, useRef, useEffect } from "react";
import { useToast } from "@/hooks/use-toast";
import { Layout } from "@/components/layout";
import { TopBar } from "@/components/top-bar";
import { FileDropzone } from "@/components/file-dropzone";
import { Document, Page, pdfjs } from "react-pdf";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { MarkdownRenderer } from "@/components/MarkdownRenderer";
import useResizeObserver from "use-resize-observer";
import {
  ProgressTracker,
  ProcessingStage,
} from "@/components/progress-tracker";
import { DownloadButtonGroup } from "@/components/download-button-group";
import { cn } from "@/lib/utils";

// Initialize PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

export default function ParseDocumentPage() {
  const [pdfPath, setPdfPath] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();
  const [isParsing, setIsParsing] = useState(false);
  const [markdownContent, setMarkdownContent] = useState<string>("");
  const [rawTextContent, setRawTextContent] = useState<string>("");
  const [layoutData, setLayoutData] = useState<object | null>(null);
  const [numPages, setNumPages] = useState<number>(0);
  const [currentStage, setCurrentStage] =
    useState<ProcessingStage>("uploading");
  const [completedStages, setCompletedStages] = useState<ProcessingStage[]>([]);
  const { ref: containerRef, width: containerWidth = 800 } =
    useResizeObserver<HTMLDivElement>();

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

  const updateStage = (stage: ProcessingStage) => {
    setCurrentStage(stage);

    // Update completed stages
    if (stage === "done") {
      setCompletedStages(["uploading", "parsing", "refining", "done"]);
    } else {
      const stageIndex = ["uploading", "parsing", "refining", "done"].indexOf(
        stage
      );
      const previousStages = ["uploading", "parsing", "refining", "done"].slice(
        0,
        stageIndex
      ) as ProcessingStage[];
      setCompletedStages(previousStages);
    }
  };

  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    setIsParsing(true);
    setMarkdownContent("");
    setRawTextContent("");
    setLayoutData(null);
    updateStage("uploading");

    // Show loading toast
    const loadingToast = toast({
      title: "Processing document",
      description: "Analyzing layout and extracting content...",
      duration: 100000, // Long duration, we'll dismiss it manually
    });

    try {
      console.log("Uploading file:", file);

      if (
        !file.name.endsWith(".pdf") &&
        !file.name.endsWith(".png") &&
        !file.name.endsWith(".jpg")
      ) {
        toast({
          title: "Unsupported file type",
          description: "Please upload a PDF or image document.",
          variant: "destructive",
        });
        return;
      }

      // Upload file to backend
      const formData = new FormData();
      formData.append("file", file);

      const uploadResponse = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error("Upload failed");
      }

      const data = await uploadResponse.json();
      setPdfPath(data.path);
      updateStage("parsing");

      // Update loading toast
      toast({
        title: "Analyzing document layout",
        description: "Detecting regions and structure...",
        duration: 100000,
      });

      // Enhanced layout analysis with direct markdown conversion
      const enhancedResponse = await fetch(
        "/api/layout/enhanced/markdown/direct/multipage",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ path: data.path }),
        }
      );

      if (!enhancedResponse.ok) {
        throw new Error("Layout analysis failed");
      }

      updateStage("refining");

      // Update loading toast
      toast({
        title: "Refining markdown output",
        description: "Cleaning and formatting the extracted content...",
        duration: 100000,
      });

      const enhancedData = await enhancedResponse.json();
      setRawTextContent(enhancedData.raw_text || "");

      // Store layout data for potential download
      setLayoutData(enhancedData.layout_data || {});

      // Refine the markdown for better display
      const refinedResponse = await fetch("/api/markdown/refine", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          markdown: enhancedData.markdown,
          raw_text: enhancedData.raw_text,
        }),
      });

      if (!refinedResponse.ok) {
        // If refinement fails, still use the original markdown
        setMarkdownContent(enhancedData.markdown);
      } else {
        const refinedData = await refinedResponse.json();
        setMarkdownContent(refinedData.markdown);
      }

      updateStage("done");

      // Success toast
      toast({
        title: "Processing complete",
        description: `${file.name} analyzed successfully.`,
        duration: 3000,
      });
    } catch (error) {
      console.error("Error:", error);
      toast({
        title: "Processing failed",
        description: "There was an error processing your document.",
        variant: "destructive",
        duration: 3000,
      });
    } finally {
      setIsUploading(false);
      setIsParsing(false);
    }
  };

  return (
    <Layout>
      <TopBar onUpload={handleUploadClick} onConfigure={handleConfigureClick} />

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
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
          <div
            className={cn(
              "transition-opacity duration-300",
              currentStage === "done" && "opacity-0 pointer-events-none"
            )}
          >
            <ProgressTracker
              currentStage={currentStage}
              completedStages={completedStages}
            />
          </div>

          <ResizablePanelGroup
            direction="horizontal"
            className="resizable-panel-container flex-1 h-full"
          >
            <ResizablePanel
              defaultSize={50}
              minSize={30}
              className="flex flex-col h-full"
            >
              <div className="h-full p-4 flex-1 flex flex-col">
                <div
                  ref={containerRef}
                  className="relative w-full h-full flex-1 overflow-auto"
                >
                  {isParsing ? (
                    <div className="absolute inset-0 flex items-center justify-center bg-background/80 z-20">
                      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
                    </div>
                  ) : null}

                  {pdfPath ? (
                    <Document
                      file={pdfPath}
                      loading={<p>Loading PDF…</p>}
                      onLoadSuccess={({ numPages }) => setNumPages(numPages)}
                    >
                      {Array.from({ length: numPages }, (_, i) => (
                        <Page
                          key={i}
                          pageNumber={i + 1}
                          width={containerWidth}
                          renderAnnotationLayer={false}
                          renderTextLayer={false}
                        />
                      ))}
                    </Document>
                  ) : (
                    <FileDropzone onFileUpload={handleFileUpload} />
                  )}
                </div>
              </div>
            </ResizablePanel>

            <ResizableHandle withHandle />

            <ResizablePanel
              defaultSize={50}
              minSize={30}
              className="flex flex-col h-full"
            >
              <div className="h-full p-4 overflow-auto flex-1 flex flex-col">
                <div className="flex justify-between items-center mb-3">
                  <h3 className="text-lg font-medium">Extracted Content</h3>
                  <DownloadButtonGroup
                    markdown={markdownContent}
                    rawText={rawTextContent}
                    layoutData={layoutData}
                    isDisabled={false}
                    path={pdfPath}
                  />
                </div>
                <div className="rounded-md border p-4 bg-background min-h-[200px] h-full overflow-auto">
                  {isParsing ? (
                    <div className="flex flex-col items-center justify-center h-full">
                      <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-primary mb-4"></div>
                      <p className="text-muted-foreground">
                        Processing document...
                      </p>
                    </div>
                  ) : markdownContent ? (
                    <MarkdownRenderer content={markdownContent} />
                  ) : (
                    <p className="text-muted-foreground text-sm">
                      Document content will appear here after processing.
                    </p>
                  )}
                </div>
              </div>
            </ResizablePanel>
          </ResizablePanelGroup>
        </div>
      )}
    </Layout>
  );
}
