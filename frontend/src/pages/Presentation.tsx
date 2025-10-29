import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ChevronLeft, ChevronRight, Home, Download } from "lucide-react";
import { GeneratedPlan } from "@/types/generator";
import LoadingState from "@/components/LoadingState";

const Presentation = () => {
  const navigate = useNavigate();
  const [plan, setPlan] = useState<GeneratedPlan | null>(null);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setTimeout(() => {
      const storedPlan = sessionStorage.getItem("finalPlan");
      if (storedPlan) {
        setPlan(JSON.parse(storedPlan));
      }
      setIsLoading(false);
    }, 1500);
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <LoadingState message="Finalizing your presentation..." />
      </div>
    );
  }

  if (!plan || plan.items.length === 0) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="p-8 text-center">
          <h2 className="text-2xl font-bold mb-4">No presentation found</h2>
          <Button onClick={() => navigate("/")}>
            <Home className="mr-2 h-4 w-4" />
            Go Home
          </Button>
        </Card>
      </div>
    );
  }

  const currentItem = plan.items[currentSlide];
  const totalSlides = plan.items.length;

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Top Bar */}
      <div className="border-b border-border/40 bg-card/80 backdrop-blur-lg px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => navigate("/")}>
              <Home className="h-4 w-4 mr-2" />
              Home
            </Button>
            <div className="text-sm text-muted-foreground">
              {plan.metadata.topic}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              {currentSlide + 1} / {totalSlides}
            </span>
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </div>
      </div>

      {/* Main Slide */}
      <div className="flex-1 flex items-center justify-center p-8">
        <Card className="w-full max-w-5xl aspect-video bg-gradient-card border-border/40 p-12 flex flex-col justify-center space-y-6 shadow-card">
          <div className="space-y-4">
            <div className="inline-block px-4 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium">
              Slide {currentSlide + 1}
            </div>
            <h1 className="text-5xl font-bold leading-tight">{currentItem.title}</h1>
          </div>
          <p className="text-xl text-muted-foreground leading-relaxed">
            {currentItem.content}
          </p>
        </Card>
      </div>

      {/* Navigation */}
      <div className="border-t border-border/40 bg-card/80 backdrop-blur-lg px-6 py-4">
        <div className="flex items-center justify-between max-w-5xl mx-auto">
          <Button
            variant="outline"
            onClick={() => setCurrentSlide(Math.max(0, currentSlide - 1))}
            disabled={currentSlide === 0}
          >
            <ChevronLeft className="h-4 w-4 mr-2" />
            Previous
          </Button>
          
          <div className="flex gap-2">
            {plan.items.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentSlide(index)}
                className={`w-2 h-2 rounded-full transition-all ${
                  index === currentSlide
                    ? "bg-primary w-8"
                    : "bg-muted-foreground/30 hover:bg-muted-foreground/50"
                }`}
              />
            ))}
          </div>

          <Button
            variant="outline"
            onClick={() => setCurrentSlide(Math.min(totalSlides - 1, currentSlide + 1))}
            disabled={currentSlide === totalSlides - 1}
          >
            Next
            <ChevronRight className="h-4 w-4 ml-2" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Presentation;
