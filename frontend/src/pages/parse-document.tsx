
import { useState, useRef } from "react";
import { useToast } from "@/hooks/use-toast";
import { Layout } from "@/components/layout";
import { TopBar } from "@/components/top-bar";
import { FileDropzone } from "@/components/file-dropzone";
import { PdfViewer } from "@/components/pdf-viewer";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";

export default function ParseDocumentPage() {
  const [file, setFile] = useState<File | null>(null);
  const [fileUrl, setFileUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const handleUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleConfigureClick = () => {
    toast({
      title: "Configure Options",
      description: "Configuration panel will be implemented in a future version.",
    });
  };

  const handleFileUpload = async (file: File) => {
    setFile(file);
    // Generate local URL for preview
    const url = URL.createObjectURL(file);
    setFileUrl(url);
    
    // In a real implementation, you would upload to the backend here
    toast({
      title: "File uploaded",
      description: `${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`,
    });
    
    // TODO: Implement actual backend upload when ready
    /*
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('/api/parse', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      setFileUrl(data.url);
    } catch (error) {
      toast({
        title: "Upload failed",
        description: "There was an error uploading your file",
        variant: "destructive",
      });
    }
    */
  };

  return (
    <Layout>
      <TopBar
        onUpload={handleUploadClick}
        onConfigure={handleConfigureClick}
      />
      
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.png,.jpg,.jpeg"
        className="hidden"
        onChange={(e) => {
          const files = e.target.files;
          if (files && files.length > 0) {
            handleFileUpload(files[0]);
          }
        }}
      />
      
      {!fileUrl ? (
        <div className="mt-8 max-w-4xl mx-auto">
          <FileDropzone onFileUpload={handleFileUpload} />
        </div>
      ) : (
        <div className="mt-8 glass-card">
          <ResizablePanelGroup
            direction="horizontal"
            className="resizable-panel-container"
          >
            <ResizablePanel defaultSize={50} minSize={30}>
              <div className="h-full p-4">
                <PdfViewer src={fileUrl} />
              </div>
            </ResizablePanel>
            
            <ResizableHandle withHandle />
            
            <ResizablePanel defaultSize={50} minSize={30}>
              <div className="h-full p-4 overflow-auto">
                <h2 className="text-xl font-semibold mb-4">Extracted Text</h2>
                <div className="rounded-md border p-4 bg-muted/30 min-h-[200px]">
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
