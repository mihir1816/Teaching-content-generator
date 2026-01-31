import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "next-themes";
import Layout from "./components/Layout";
import Landing from "./pages/Landing";
import SelectOption from "./pages/SelectOption";
import TopicOnly from "./pages/generate/TopicOnly";
import YouTube from "./pages/generate/YouTube";
import Article from "./pages/generate/Article";
import Document from "./pages/generate/Document";
import Combined from "./pages/generate/Combined";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Layout>
            <Routes>
              <Route path="/" element={<Landing />} />
              <Route path="/select" element={<SelectOption />} />
              <Route path="/generate/topic" element={<TopicOnly />} />
              <Route path="/generate/youtube" element={<YouTube />} />
              <Route path="/generate/article" element={<Article />} />
              <Route path="/generate/document" element={<Document />} />
              <Route path="/generate/combined" element={<Combined />} />
              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Layout>
        </BrowserRouter>
      </TooltipProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;
