
import { Button } from "./ui/button";
import { Upload, Cog } from "lucide-react";
import { cn } from "@/lib/utils";

interface TopBarProps {
  onUpload: () => void;
  onConfigure: () => void;
  className?: string;
}

export function TopBar({ onUpload, onConfigure, className }: TopBarProps) {
  return (
    <div className={cn("flex items-center justify-between py-4 px-4", className)}>
      <Button onClick={onUpload} className="bg-marine hover:bg-marine-light">
        <Upload className="mr-2 h-4 w-4" />
        Choose File
      </Button>
      
      <div className="flex items-center">
        <Button variant="ghost" size="icon" onClick={onConfigure} className="rounded-full">
          <Cog className="h-5 w-5" />
          <span className="sr-only">Configure Options</span>
        </Button>
      </div>
    </div>
  );
}
