
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import ParseDocumentPage from "./pages/parse-document";
import ExtractDataPage from "./pages/extract-data";
import NotFoundPage from "./pages/not-found";
import { useEffect } from "react";

const queryClient = new QueryClient();

const App = () => {
  // Initialize theme from localStorage or use dark as default
  useEffect(() => {
    const storedTheme = localStorage.getItem("theme") || "dark";
    document.documentElement.classList.toggle("dark", storedTheme === "dark");
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<ParseDocumentPage />} />
            <Route path="/extract" element={<ExtractDataPage />} />
            <Route path="/404" element={<NotFoundPage />} />
            <Route path="*" element={<Navigate to="/404" replace />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;
