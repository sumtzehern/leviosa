
import { useState, useCallback } from "react";
import { Upload } from "lucide-react";
import { useToast } from "../hooks/use-toast";

interface FileDropzoneProps {
  onFileUpload: (file: File) => void;
}

export function FileDropzone({ onFileUpload }: FileDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const { toast } = useToast();
  
  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);
      
      const files = e.dataTransfer.files;
      
      if (files.length > 0) {
        const file = files[0];
        validateAndUploadFile(file);
      }
    },
    [onFileUpload]
  );

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      
      if (files && files.length > 0) {
        const file = files[0];
        validateAndUploadFile(file);
      }
    },
    [onFileUpload]
  );

  const validateAndUploadFile = (file: File) => {
    const allowedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
    const maxSize = 1024 * 1024 * 1024; // 1GB
    
    if (!allowedTypes.includes(file.type)) {
      toast({
        title: "Invalid file type",
        description: "Please upload a PDF, PNG, or JPG file.",
        variant: "destructive",
      });
      return;
    }
    
    if (file.size > maxSize) {
      toast({
        title: "File too large",
        description: "Please upload a file smaller than 1GB.",
        variant: "destructive",
      });
      return;
    }
    
    onFileUpload(file);
  };

  return (
    <div
      className={`border-2 border-dashed rounded-xl p-12 flex flex-col items-center justify-center transition-colors cursor-pointer h-full min-h-[300px]
        ${isDragging ? 'border-primary bg-primary/5' : 'border-muted-foreground/20'}
        hover:border-primary/50 hover:bg-muted/50`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => document.getElementById('file-input')?.click()}
    >
      <input
        id="file-input"
        type="file"
        className="hidden"
        accept=".pdf,.png,.jpg,.jpeg"
        onChange={handleFileChange}
      />
      
      <div className="w-16 h-16 mb-4 rounded-full bg-primary/10 flex items-center justify-center">
        <Upload className="h-8 w-8 text-primary" />
      </div>
      
      <h3 className="text-lg font-medium mb-2">Choose files or drag and drop</h3>
      <p className="text-sm text-muted-foreground text-center">
        PDF, Image, Office File (1GB)
      </p>
      <p className="text-xs text-muted-foreground mt-8 text-center">
        Click to go back, hold to see history
      </p>
    </div>
  );
}
