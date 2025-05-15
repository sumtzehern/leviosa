
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { DownloadIcon } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface DownloadButtonGroupProps {
  markdown?: string;
  rawText?: string;
  layoutData?: object;
  isDisabled?: boolean;
}

export function DownloadButtonGroup({
  markdown,
  rawText,
  layoutData,
  isDisabled = false,
}: DownloadButtonGroupProps) {
  const [isDownloading, setIsDownloading] = useState(false);

  const downloadFile = (content: string, filename: string, type: string) => {
    setIsDownloading(true);
    try {
      const blob = new Blob([content], { type });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Download failed:", error);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="secondary"
          size="sm"
          className="gap-2"
          disabled={isDisabled || isDownloading}
        >
          <DownloadIcon size={16} />
          Download
          {isDownloading && (
            <span className="ml-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem
          disabled={!markdown}
          onClick={() => markdown && downloadFile(markdown, "document.md", "text/markdown")}
        >
          Download as Markdown (.md)
        </DropdownMenuItem>
        <DropdownMenuItem
          disabled={!rawText}
          onClick={() => rawText && downloadFile(rawText, "raw-text.txt", "text/plain")}
        >
          Download Raw Text (.txt)
        </DropdownMenuItem>
        <DropdownMenuItem
          disabled={!layoutData}
          onClick={() => 
            layoutData && 
            downloadFile(
              JSON.stringify(layoutData, null, 2),
              "layout-data.json",
              "application/json"
            )
          }
        >
          Download Layout Data (.json)
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
