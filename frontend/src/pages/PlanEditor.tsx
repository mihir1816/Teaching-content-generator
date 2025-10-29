// import { useState, useEffect } from "react";
// import { useNavigate } from "react-router-dom";
// import Navbar from "@/components/Navbar";
// import LoadingState from "@/components/LoadingState";
// import { Button } from "@/components/ui/button";
// import { Card } from "@/components/ui/card";
// import { Textarea } from "@/components/ui/textarea";
// import { Sparkles } from "lucide-react";
// import { GeneratedPlan } from "@/types/generator";

// const PlanEditor = () => {
//   const navigate = useNavigate();
//   const [isGenerating, setIsGenerating] = useState(true);
//   const [plan, setPlan] = useState<GeneratedPlan | null>(null);
//   const [planText, setPlanText] = useState("");
//   const [isCreatingContent, setIsCreatingContent] = useState(false);
//   const [isRegenerating, setIsRegenerating] = useState(false);

//   useEffect(() => {
//     // Simulate plan generation
//     setTimeout(() => {
//       const storedData = sessionStorage.getItem("generatorData");
//       const data = storedData ? JSON.parse(storedData) : {};
      
//       // Mock generated plan
//       const mockPlan: GeneratedPlan = {
//         items: [
//           { id: "1", title: "Introduction", content: "Overview of the topic and learning objectives", order: 1 },
//           { id: "2", title: "Core Concepts", content: "Main concepts and theoretical framework", order: 2 },
//           { id: "3", title: "Practical Examples", content: "Real-world applications and case studies", order: 3 },
//           { id: "4", title: "Key Takeaways", content: "Summary and important points to remember", order: 4 },
//         ],
//         metadata: {
//           topic: data.topic || "Sample Topic",
//           level: data.level || "intermediate",
//           style: data.style || "detailed",
//         }
//       };
      
//       setPlan(mockPlan);
      
//       // Convert plan to text format
//       const text = mockPlan.items
//         .map((item, idx) => `Slide ${idx + 1}: ${item.title}\n${item.content}`)
//         .join("\n\n");
//       setPlanText(text);
      
//       setIsGenerating(false);
//     }, 2000);
//   }, []);

//   const handleEditPlan = () => {
//     setIsRegenerating(true);
    
//     // Simulate backend regenerating plan based on edited text
//     setTimeout(() => {
//       const storedData = sessionStorage.getItem("generatorData");
//       const data = storedData ? JSON.parse(storedData) : {};
      
//       // Mock regenerated plan with some variations
//       const regeneratedPlan: GeneratedPlan = {
//         items: [
//           { id: "1", title: "Updated Introduction", content: "Refined overview with enhanced learning objectives", order: 1 },
//           { id: "2", title: "Enhanced Core Concepts", content: "Expanded theoretical framework with examples", order: 2 },
//           { id: "3", title: "Advanced Examples", content: "More detailed real-world applications", order: 3 },
//           { id: "4", title: "Comprehensive Summary", content: "Extended takeaways and next steps", order: 4 },
//         ],
//         metadata: {
//           topic: data.topic || "Sample Topic",
//           level: data.level || "intermediate",
//           style: data.style || "detailed",
//         }
//       };
      
//       setPlan(regeneratedPlan);
      
//       const text = regeneratedPlan.items
//         .map((item, idx) => `Slide ${idx + 1}: ${item.title}\n${item.content}`)
//         .join("\n\n");
//       setPlanText(text);
      
//       setIsRegenerating(false);
//     }, 2000);
//   };

//   const handleGenerateContent = () => {
//     setIsCreatingContent(true);
    
//     // Parse the text back into plan format
//     const lines = planText.split("\n\n");
//     const parsedItems = lines.map((section, idx) => {
//       const titleMatch = section.match(/Slide \d+: (.+)/);
//       const title = titleMatch ? titleMatch[1] : `Slide ${idx + 1}`;
//       const content = section.split("\n").slice(1).join("\n") || "Content";
      
//       return {
//         id: (idx + 1).toString(),
//         title,
//         content,
//         order: idx + 1,
//       };
//     });
    
//     const updatedPlan = {
//       ...plan!,
//       items: parsedItems,
//     };
    
//     sessionStorage.setItem("finalPlan", JSON.stringify(updatedPlan));
//     setTimeout(() => {
//       navigate("/presentation");
//     }, 2000);
//   };

//   if (isGenerating) {
//     return (
//       <div className="min-h-screen bg-background">
//         <Navbar />
//         <LoadingState message="Generating your presentation plan..." />
//       </div>
//     );
//   }

//   if (isRegenerating) {
//     return (
//       <div className="min-h-screen bg-background">
//         <Navbar />
//         <LoadingState message="Regenerating your plan..." />
//       </div>
//     );
//   }

//   if (isCreatingContent) {
//     return (
//       <div className="min-h-screen bg-background">
//         <Navbar />
//         <LoadingState message="Creating your presentation slides..." />
//       </div>
//     );
//   }

//   return (
//     <div className="min-h-screen bg-background">
//       <Navbar />
//       <div className="pt-24 pb-12 px-4">
//         <div className="container mx-auto max-w-4xl">
//           <div className="text-center mb-8">
//             <h1 className="text-4xl font-bold mb-4">Edit Your Plan</h1>
//             <p className="text-muted-foreground">
//               Review and customize the generated presentation structure
//             </p>
//             <div className="flex items-center justify-center gap-4 mt-4">
//               <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-sm">
//                 {plan?.metadata.level}
//               </span>
//               <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-sm">
//                 {plan?.metadata.style}
//               </span>
//             </div>
//           </div>

//           <Card className="p-6 bg-gradient-card border-border/40 mb-6">
//             <Textarea
//               value={planText}
//               onChange={(e) => setPlanText(e.target.value)}
//               className="bg-background/50 min-h-[500px] text-base font-mono resize-none"
//               placeholder="Edit your presentation plan here..."
//             />
//           </Card>

//           <div className="flex gap-4">
//             <Button
//               onClick={handleEditPlan}
//               variant="outline"
//               className="flex-1"
//             >
//               <Sparkles className="mr-2 h-5 w-5" />
//               Edit Plan
//             </Button>
//             <Button
//               onClick={handleGenerateContent}
//               className="flex-1 bg-gradient-accent shadow-glow hover:shadow-glow/50"
//             >
//               <Sparkles className="mr-2 h-5 w-5" />
//               Generate Content
//             </Button>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default PlanEditor;

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Sparkles, Loader2 } from "lucide-react";

interface PlanMetadata {
  topic: string;
  level: string;
  style: string;
}

const PlanEditor = () => {
  const [isGenerating, setIsGenerating] = useState(true);
  const [planText, setPlanText] = useState("");
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [isCreatingContent, setIsCreatingContent] = useState(false);
  const [metadata, setMetadata] = useState<PlanMetadata | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Load the generated plan from sessionStorage
    setTimeout(() => {
      const storedPlan = sessionStorage.getItem("generatedPlan");
      const storedData = sessionStorage.getItem("generatorData");
      
      if (storedPlan && storedData) {
        const data = JSON.parse(storedData);
        setMetadata({
          topic: data.topic,
          level: data.level,
          style: data.style,
        });
        
        // The API response is stored as-is
        // Convert it to editable text format
        setPlanText(storedPlan);
      } else {
        setError("No plan data found. Please generate a plan first.");
      }
      
      setIsGenerating(false);
    }, 500);
  }, []);

  const handleRegeneratePlan = async () => {
    if (!metadata) return;
    
    setIsRegenerating(true);
    setError(null);

    try {
      const payload = {
        level: metadata.level,
        style: metadata.style,
        topics: metadata.topic,
        description: planText, // Send edited text as description
        language: "en",
      };

      const response = await fetch("http://localhost:5000/api/plan/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || "Failed to regenerate plan");
      }

      // Update with new plan
      setPlanText(JSON.stringify(result.data, null, 2));
      sessionStorage.setItem("generatedPlan", JSON.stringify(result.data));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to regenerate plan");
    } finally {
      setIsRegenerating(false);
    }
  };

  const handleGenerateContent = () => {
    setIsCreatingContent(true);
    
    // Store the final edited plan
    sessionStorage.setItem("finalPlan", planText);
    
    // Simulate content generation and redirect
    setTimeout(() => {
      if (window.location) {
        window.location.href = "/presentation";
      }
    }, 2000);
  };

  if (isGenerating) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-slate-300 text-lg">Loading your plan...</p>
        </div>
      </div>
    );
  }

  if (error && !metadata) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
        <Card className="p-8 bg-red-900/20 border-red-500/30 max-w-md">
          <h3 className="text-xl font-semibold text-red-400 mb-2">Error</h3>
          <p className="text-red-300 mb-4">{error}</p>
          <Button
            onClick={() => window.location.href = "/"}
            className="w-full bg-blue-600 hover:bg-blue-700"
          >
            Go Back to Generator
          </Button>
        </Card>
      </div>
    );
  }

  if (isRegenerating) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-slate-300 text-lg">Regenerating your plan...</p>
        </div>
      </div>
    );
  }

  if (isCreatingContent) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-slate-300 text-lg">Creating your presentation slides...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <div className="pt-12 pb-12 px-4">
        <div className="container mx-auto max-w-4xl">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold mb-4 text-white">Edit Your Plan</h1>
            <p className="text-slate-400">
              Review and customize the generated presentation structure
            </p>
            {metadata && (
              <div className="flex items-center justify-center gap-4 mt-4">
                <span className="px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 text-sm border border-blue-500/30">
                  {metadata.topic}
                </span>
                <span className="px-3 py-1 rounded-full bg-purple-500/10 text-purple-400 text-sm border border-purple-500/30">
                  {metadata.level}
                </span>
                <span className="px-3 py-1 rounded-full bg-green-500/10 text-green-400 text-sm border border-green-500/30">
                  {metadata.style}
                </span>
              </div>
            )}
          </div>

          {error && (
            <Card className="p-4 bg-red-900/20 border-red-500/30 mb-6">
              <p className="text-red-300 text-sm">{error}</p>
            </Card>
          )}

          <Card className="p-6 bg-slate-800/50 border-slate-700 mb-6">
            <Textarea
              value={planText}
              onChange={(e) => setPlanText(e.target.value)}
              className="bg-slate-900/50 border-slate-700 text-white placeholder:text-slate-500 min-h-[500px] text-base font-mono resize-none"
              placeholder="Edit your presentation plan here..."
            />
          </Card>

          <div className="flex gap-4">
            <Button
              onClick={handleRegeneratePlan}
              variant="outline"
              className="flex-1 border-slate-600 text-slate-300 hover:bg-slate-700 hover:text-white"
              disabled={isRegenerating}
            >
              {isRegenerating ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Regenerating...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-5 w-5" />
                  Regenerate Plan
                </>
              )}
            </Button>
            <Button
              onClick={handleGenerateContent}
              className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg hover:shadow-xl transition-all"
              disabled={isCreatingContent}
            >
              {isCreatingContent ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-5 w-5" />
                  Generate Content
                </>
              )}
            </Button>
          </div>

          <div className="mt-6 text-center">
            <Button
              variant="ghost"
              onClick={() => window.location.href = "/"}
              className="text-slate-400 hover:text-white"
            >
              ← Back to Generator
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlanEditor;