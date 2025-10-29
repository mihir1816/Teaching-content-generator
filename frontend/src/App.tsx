import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Landing from "./pages/Landing";
import FullGenerator from "./pages/FullGenerator";
import TopicGenerator from "./pages/TopicGenerator";
import YouTubeGenerator from "./pages/YouTubeGenerator";
import DocumentGenerator from "./pages/DocumentGenerator";
import PlanEditor from "./pages/PlanEditor";
import Presentation from "./pages/Presentation";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/generate/full" element={<FullGenerator />} />
          <Route path="/generate/topic" element={<TopicGenerator />} />
          <Route path="/generate/youtube" element={<YouTubeGenerator />} />
          <Route path="/generate/document" element={<DocumentGenerator />} />
          <Route path="/plan-editor" element={<PlanEditor />} />
          <Route path="/presentation" element={<Presentation />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
