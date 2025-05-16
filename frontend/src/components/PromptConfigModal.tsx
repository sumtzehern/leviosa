// components/PromptConfigModal.tsx
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

interface PromptConfigModalProps {
  open: boolean;
  onClose: () => void;
  prompt: string;
  setPrompt: (value: string) => void;
}

export function PromptConfigModal({ open, onClose, prompt, setPrompt }: PromptConfigModalProps) {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Custom Parsing Prompt</DialogTitle>
        </DialogHeader>
        <Textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="e.g. Extract only tables and output as clean Markdown..."
          rows={5}
        />
        <DialogFooter className="pt-4">
          <Button onClick={onClose}>Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
