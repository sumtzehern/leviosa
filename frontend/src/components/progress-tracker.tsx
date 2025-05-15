
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

  // Calculate progress percentage
  const stageIndex = stages.findIndex(stage => stage.id === currentStage);
  const progressValue = ((stageIndex + 1) / stages.length) * 100;

  return (
    <div className="w-full space-y-2 mb-6">
      <Progress value={progressValue} className="h-2" />
      
      <div className="flex justify-between">
        {stages.map((stage) => {
          const isActive = currentStage === stage.id;
          const isCompleted = completedStages.includes(stage.id);
          
          return (
            <div 
              key={stage.id} 
              className="flex flex-col items-center"
            >
              <div 
                className={cn(
                  "flex items-center justify-center w-8 h-8 rounded-full border",
                  isActive && "bg-primary border-primary text-primary-foreground",
                  isCompleted && "bg-primary/80 border-primary/80 text-primary-foreground",
                  !isActive && !isCompleted && "bg-secondary border-secondary text-secondary-foreground"
                )}
              >
                {isCompleted ? (
                  <Check size={16} />
                ) : (
                  <span className="text-xs">{stages.indexOf(stage) + 1}</span>
                )}
              </div>
              <span 
                className={cn(
                  "text-xs mt-1",
                  isActive && "text-primary font-medium",
                  isCompleted && "text-primary/80 font-medium"
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
