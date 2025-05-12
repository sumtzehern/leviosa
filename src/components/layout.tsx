
import { ReactNode } from "react";
import { Sidebar } from "./sidebar";
import { cn } from "@/lib/utils";

interface LayoutProps {
  children: ReactNode;
  className?: string;
}

export function Layout({ children, className }: LayoutProps) {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className={cn("flex-1 ml-0 md:ml-60 transition-all", className)}>
        <div className="container py-4 max-w-[1400px]">
          {children}
        </div>
      </main>
    </div>
  );
}
