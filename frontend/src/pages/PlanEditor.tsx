import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import LoadingState from "@/components/LoadingState";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Sparkles } from "lucide-react";
import { GeneratedPlan } from "@/types/generator";

const PlanEditor = () => {
  const navigate = useNavigate();
  const [isGenerating, setIsGenerating] = useState(true);
  const [plan, setPlan] = useState<GeneratedPlan | null>(null);
  const [planText, setPlanText] = useState("");
  const [isCreatingContent, setIsCreatingContent] = useState(false);
  const [isRegenerating, setIsRegenerating] = useState(false);

  useEffect(() => {
    // Simulate plan generation
    setTimeout(() => {
      const storedData = sessionStorage.getItem("generatorData");
      const data = storedData ? JSON.parse(storedData) : {};
      
      // Mock generated plan
      const mockPlan: GeneratedPlan = {
        items: [
          { id: "1", title: "Introduction", content: "Overview of the topic and learning objectives", order: 1 },
          { id: "2", title: "Core Concepts", content: "Main concepts and theoretical framework", order: 2 },
          { id: "3", title: "Practical Examples", content: "Real-world applications and case studies", order: 3 },
          { id: "4", title: "Key Takeaways", content: "Summary and important points to remember", order: 4 },
        ],
        metadata: {
          topic: data.topic || "Sample Topic",
          level: data.level || "intermediate",
          style: data.style || "detailed",
        }
      };
      
      setPlan(mockPlan);
      
      // Convert plan to text format
      const text = mockPlan.items
        .map((item, idx) => `Slide ${idx + 1}: ${item.title}\n${item.content}`)
        .join("\n\n");
      setPlanText(text);
      
      setIsGenerating(false);
    }, 2000);
  }, []);

  const handleEditPlan = () => {
    setIsRegenerating(true);
    
    // Simulate backend regenerating plan based on edited text
    setTimeout(() => {
      const storedData = sessionStorage.getItem("generatorData");
      const data = storedData ? JSON.parse(storedData) : {};
      
      // Mock regenerated plan with some variations
      const regeneratedPlan: GeneratedPlan = {
        items: [
          { id: "1", title: "Updated Introduction", content: "Refined overview with enhanced learning objectives", order: 1 },
          { id: "2", title: "Enhanced Core Concepts", content: "Expanded theoretical framework with examples", order: 2 },
          { id: "3", title: "Advanced Examples", content: "More detailed real-world applications", order: 3 },
          { id: "4", title: "Comprehensive Summary", content: "Extended takeaways and next steps", order: 4 },
        ],
        metadata: {
          topic: data.topic || "Sample Topic",
          level: data.level || "intermediate",
          style: data.style || "detailed",
        }
      };
      
      setPlan(regeneratedPlan);
      
      const text = regeneratedPlan.items
        .map((item, idx) => `Slide ${idx + 1}: ${item.title}\n${item.content}`)
        .join("\n\n");
      setPlanText(text);
      
      setIsRegenerating(false);
    }, 2000);
  };

  const handleGenerateContent = () => {
    setIsCreatingContent(true);
    
    // Parse the text back into plan format
    const lines = planText.split("\n\n");
    const parsedItems = lines.map((section, idx) => {
      const titleMatch = section.match(/Slide \d+: (.+)/);
      const title = titleMatch ? titleMatch[1] : `Slide ${idx + 1}`;
      const content = section.split("\n").slice(1).join("\n") || "Content";
      
      return {
        id: (idx + 1).toString(),
        title,
        content,
        order: idx + 1,
      };
    });
    
    const updatedPlan = {
      ...plan!,
      items: parsedItems,
    };
    
    sessionStorage.setItem("finalPlan", JSON.stringify(updatedPlan));
    setTimeout(() => {
      navigate("/presentation");
    }, 2000);
  };

  if (isGenerating) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <LoadingState message="Generating your presentation plan..." />
      </div>
    );
  }

  if (isRegenerating) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <LoadingState message="Regenerating your plan..." />
      </div>
    );
  }

  if (isCreatingContent) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <LoadingState message="Creating your presentation slides..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="pt-24 pb-12 px-4">
        <div className="container mx-auto max-w-4xl">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold mb-4">Edit Your Plan</h1>
            <p className="text-muted-foreground">
              Review and customize the generated presentation structure
            </p>
            <div className="flex items-center justify-center gap-4 mt-4">
              <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-sm">
                {plan?.metadata.level}
              </span>
              <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-sm">
                {plan?.metadata.style}
              </span>
            </div>
          </div>

          <Card className="p-6 bg-gradient-card border-border/40 mb-6">
            <Textarea
              value={planText}
              onChange={(e) => setPlanText(e.target.value)}
              className="bg-background/50 min-h-[500px] text-base font-mono resize-none"
              placeholder="Edit your presentation plan here..."
            />
          </Card>

          <div className="flex gap-4">
            <Button
              onClick={handleEditPlan}
              variant="outline"
              className="flex-1"
            >
              <Sparkles className="mr-2 h-5 w-5" />
              Edit Plan
            </Button>
            <Button
              onClick={handleGenerateContent}
              className="flex-1 bg-gradient-accent shadow-glow hover:shadow-glow/50"
            >
              <Sparkles className="mr-2 h-5 w-5" />
              Generate Content
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlanEditor;
