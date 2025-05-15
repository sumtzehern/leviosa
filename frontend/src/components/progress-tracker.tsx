
import { Check } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

export type ProcessingStage = "uploading" | "parsing" | "refining" | "done";

interface ProgressTrackerProps {
  currentStage: ProcessingStage;
  completedStages: ProcessingStage[];
}

export function ProgressTracker({ 
  currentStage, 
  completedStages 
}: ProgressTrackerProps) {
  const stages: { id: ProcessingStage; label: string }[] = [
    { id: "uploading", label: "Uploading" },
    { id: "parsing", label: "Parsing" },
    { id: "refining", label: "Refining" },
    { id: "done", label: "Done" }
  ];

  const stageIndex = stages.findIndex(stage => stage.id === currentStage);
  const progressValue = ((stageIndex + 1) / stages.length) * 100;

  return (
    <div className="w-full space-y-1 mb-4">
      <Progress value={progressValue} className="h-1 bg-green-100" />

      <div className="flex justify-between px-2">
        {stages.map((stage) => {
          const isActive = currentStage === stage.id;
          const isCompleted = completedStages.includes(stage.id);
          
          return (
            <div key={stage.id} className="flex flex-col items-center space-y-1">
              <div
                className={cn(
                  "flex items-center justify-center w-5 h-5 rounded-full border text-[10px]",
                  isCompleted
                    ? "bg-green-500 border-green-500 text-white"
                    : isActive
                    ? "bg-green-600 border-green-600 text-white"
                    : "bg-muted text-muted-foreground border border-muted"
                )}
              >
                {isCompleted ? <Check size={12} /> : <span>{stages.indexOf(stage) + 1}</span>}
              </div>
              <span
                className={cn(
                  "text-[10px] font-medium text-muted-foreground",
                  isActive && "text-green-600",
                  isCompleted && "text-green-500"
                )}
              >
                {stage.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}