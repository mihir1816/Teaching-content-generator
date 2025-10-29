// import { useState } from "react";
// import { Button } from "@/components/ui/button";
// import { Input } from "@/components/ui/input";
// import { Label } from "@/components/ui/label";
// import { Textarea } from "@/components/ui/textarea";
// import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
// import { Card } from "@/components/ui/card";
// import { Upload, Youtube, FileText } from "lucide-react";
// import { GeneratorFormData, Level, Style } from "@/types/generator";

// interface GeneratorFormProps {
//   variant: "full" | "topic" | "youtube" | "document";
//   onSubmit: (data: GeneratorFormData) => void;
//   isLoading: boolean;
// }

// const GeneratorForm = ({ variant, onSubmit, isLoading }: GeneratorFormProps) => {
//   const [formData, setFormData] = useState<GeneratorFormData>({
//     topic: "",
//     description: "",
//     youtubeLink: "",
//     level: "intermediate",
//     style: "detailed",
//   });

//   const handleSubmit = (e: React.FormEvent) => {
//     e.preventDefault();
//     onSubmit(formData);
//   };

//   const showYouTube = variant === "full" || variant === "youtube";
//   const showDocuments = variant === "full" || variant === "document";

//   return (
//     <Card className="p-8 bg-gradient-card border-border/40">
//       <form onSubmit={handleSubmit} className="space-y-6">
//         {/* Topic */}
//         <div className="space-y-2">
//           <Label htmlFor="topic" className="flex items-center gap-2">
//             <FileText className="h-4 w-4 text-primary" />
//             Topic Name *
//           </Label>
//           <Input
//             id="topic"
//             placeholder="Enter your topic..."
//             value={formData.topic}
//             onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
//             required
//             className="bg-background/50"
//           />
//         </div>

//         {/* Description */}
//         <div className="space-y-2">
//           <Label htmlFor="description">Topic Description</Label>
//           <Textarea
//             id="description"
//             placeholder="Provide more details about your topic..."
//             value={formData.description}
//             onChange={(e) => setFormData({ ...formData, description: e.target.value })}
//             className="bg-background/50 min-h-24"
//           />
//         </div>

//         {/* YouTube Link */}
//         {showYouTube && (
//           <div className="space-y-2">
//             <Label htmlFor="youtube" className="flex items-center gap-2">
//               <Youtube className="h-4 w-4 text-primary" />
//               YouTube Link {variant !== "youtube" && "(Optional)"}
//             </Label>
//             <Input
//               id="youtube"
//               type="url"
//               placeholder="https://youtube.com/watch?v=..."
//               value={formData.youtubeLink}
//               onChange={(e) => setFormData({ ...formData, youtubeLink: e.target.value })}
//               required={variant === "youtube"}
//               className="bg-background/50"
//             />
//           </div>
//         )}

//         {/* Documents */}
//         {showDocuments && (
//           <div className="space-y-2">
//             <Label htmlFor="documents" className="flex items-center gap-2">
//               <Upload className="h-4 w-4 text-primary" />
//               Upload Documents {variant !== "document" && "(Optional)"}
//             </Label>
//             <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary/50 transition-colors bg-background/30">
//               <Upload className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
//               <p className="text-sm text-muted-foreground mb-2">
//                 Click to upload or drag and drop
//               </p>
//               <Input
//                 id="documents"
//                 type="file"
//                 multiple
//                 className="hidden"
//                 onChange={(e) => {
//                   const files = Array.from(e.target.files || []);
//                   setFormData({ ...formData, documents: files });
//                 }}
//               />
//               <Button
//                 type="button"
//                 variant="outline"
//                 size="sm"
//                 onClick={() => document.getElementById("documents")?.click()}
//               >
//                 Select Files
//               </Button>
//             </div>
//           </div>
//         )}

//         {/* Level */}
//         <div className="space-y-2">
//           <Label htmlFor="level">Difficulty Level *</Label>
//           <Select
//             value={formData.level}
//             onValueChange={(value: Level) => setFormData({ ...formData, level: value })}
//           >
//             <SelectTrigger className="bg-background/50">
//               <SelectValue />
//             </SelectTrigger>
//             <SelectContent>
//               <SelectItem value="beginner">Beginner</SelectItem>
//               <SelectItem value="intermediate">Intermediate</SelectItem>
//               <SelectItem value="advanced">Advanced</SelectItem>
//             </SelectContent>
//           </Select>
//         </div>

//         {/* Style */}
//         <div className="space-y-2">
//           <Label htmlFor="style">Presentation Style *</Label>
//           <Select
//             value={formData.style}
//             onValueChange={(value: Style) => setFormData({ ...formData, style: value })}
//           >
//             <SelectTrigger className="bg-background/50">
//               <SelectValue />
//             </SelectTrigger>
//             <SelectContent>
//               <SelectItem value="concise">Concise</SelectItem>
//               <SelectItem value="detailed">Detailed</SelectItem>
//               <SelectItem value="exam-prep">Exam Preparation</SelectItem>
//             </SelectContent>
//           </Select>
//         </div>

//         {/* Submit Button */}
//         <Button
//           type="submit"
//           className="w-full bg-gradient-accent shadow-glow hover:shadow-glow/50"
//           disabled={isLoading}
//         >
//           {isLoading ? "Generating..." : "Generate Plan"}
//         </Button>
//       </form>
//     </Card>
//   );
// };

// export default GeneratorForm;
// import { useState } from "react";
// import { Button } from "@/components/ui/button";
// import { Input } from "@/components/ui/input";
// import { Label } from "@/components/ui/label";
// import { Textarea } from "@/components/ui/textarea";
// import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
// import { Card } from "@/components/ui/card";
// import { Upload, Youtube, FileText } from "lucide-react";

// type Level = "beginner" | "intermediate" | "advanced";
// type Style = "concise" | "detailed" | "exam-prep";

// interface GeneratorFormData {
//   topic: string;
//   description: string;
//   youtubeLink: string;
//   level: Level;
//   style: Style;
//   documents?: File[];
// }

// interface GeneratorFormProps {
//   variant: "full" | "topic" | "youtube" | "document";
//   onSubmit?: (data: GeneratorFormData) => void;
//   isLoading?: boolean;
// }

// const GeneratorForm = ({ variant, onSubmit, isLoading = false }: GeneratorFormProps) => {
//   const [formData, setFormData] = useState<GeneratorFormData>({
//     topic: "",
//     description: "",
//     youtubeLink: "",
//     level: "intermediate",
//     style: "detailed",
//   });
//   const [apiLoading, setApiLoading] = useState(false);
//   const [apiResponse, setApiResponse] = useState<any>(null);
//   const [apiError, setApiError] = useState<string | null>(null);

//   const handleSubmit = async (e: React.FormEvent) => {
//     e.preventDefault();
    
//     // If parent provided onSubmit, use that
//     if (onSubmit) {
//       onSubmit(formData);
//       return;
//     }

//     // Otherwise, call the API directly
//     setApiLoading(true);
//     setApiError(null);
//     setApiResponse(null);

//     try {
//       const payload = {
//         level: formData.level,
//         style: formData.style,
//         topics: formData.topic,
//         description: formData.description,
//         language: "en",
//         model_name: "gpt-4" // You can make this configurable
//       };

//       const response = await fetch("/api/plan/generate", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify(payload),
//       });

//       const result = await response.json();

//       if (!response.ok) {
//         throw new Error(result.message || "Failed to generate plan");
//       }

//       setApiResponse(result);
//     } catch (error) {
//       setApiError(error instanceof Error ? error.message : "An error occurred");
//     } finally {
//       setApiLoading(false);
//     }
//   };

//   const showYouTube = variant === "full" || variant === "youtube";
//   const showDocuments = variant === "full" || variant === "document";
//   const loading = isLoading || apiLoading;

//   return (
//     <div className="space-y-6">
//       <Card className="p-8 bg-gradient-to-br from-slate-50 to-white border-slate-200">
//         <form onSubmit={handleSubmit} className="space-y-6">
//           {/* Topic */}
//           <div className="space-y-2">
//             <Label htmlFor="topic" className="flex items-center gap-2">
//               <FileText className="h-4 w-4 text-blue-600" />
//               Topic Name *
//             </Label>
//             <Input
//               id="topic"
//               placeholder="Enter your topic..."
//               value={formData.topic}
//               onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
//               required
//               className="bg-white/50"
//             />
//           </div>

//           {/* Description */}
//           <div className="space-y-2">
//             <Label htmlFor="description">Topic Description</Label>
//             <Textarea
//               id="description"
//               placeholder="Provide more details about your topic..."
//               value={formData.description}
//               onChange={(e) => setFormData({ ...formData, description: e.target.value })}
//               className="bg-white/50 min-h-24"
//             />
//           </div>

//           {/* YouTube Link */}
//           {showYouTube && (
//             <div className="space-y-2">
//               <Label htmlFor="youtube" className="flex items-center gap-2">
//                 <Youtube className="h-4 w-4 text-blue-600" />
//                 YouTube Link {variant !== "youtube" && "(Optional)"}
//               </Label>
//               <Input
//                 id="youtube"
//                 type="url"
//                 placeholder="https://youtube.com/watch?v=..."
//                 value={formData.youtubeLink}
//                 onChange={(e) => setFormData({ ...formData, youtubeLink: e.target.value })}
//                 required={variant === "youtube"}
//                 className="bg-white/50"
//               />
//             </div>
//           )}

//           {/* Documents */}
//           {showDocuments && (
//             <div className="space-y-2">
//               <Label htmlFor="documents" className="flex items-center gap-2">
//                 <Upload className="h-4 w-4 text-blue-600" />
//                 Upload Documents {variant !== "document" && "(Optional)"}
//               </Label>
//               <div className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors bg-white/30">
//                 <Upload className="h-8 w-8 text-slate-400 mx-auto mb-2" />
//                 <p className="text-sm text-slate-600 mb-2">
//                   Click to upload or drag and drop
//                 </p>
//                 <Input
//                   id="documents"
//                   type="file"
//                   multiple
//                   className="hidden"
//                   onChange={(e) => {
//                     const files = Array.from(e.target.files || []);
//                     setFormData({ ...formData, documents: files });
//                   }}
//                 />
//                 <Button
//                   type="button"
//                   variant="outline"
//                   size="sm"
//                   onClick={() => document.getElementById("documents")?.click()}
//                 >
//                   Select Files
//                 </Button>
//                 {formData.documents && formData.documents.length > 0 && (
//                   <p className="text-xs text-slate-600 mt-2">
//                     {formData.documents.length} file(s) selected
//                   </p>
//                 )}
//               </div>
//             </div>
//           )}

//           {/* Level */}
//           <div className="space-y-2">
//             <Label htmlFor="level">Difficulty Level *</Label>
//             <Select
//               value={formData.level}
//               onValueChange={(value: Level) => setFormData({ ...formData, level: value })}
//             >
//               <SelectTrigger className="bg-white/50">
//                 <SelectValue />
//               </SelectTrigger>
//               <SelectContent>
//                 <SelectItem value="beginner">Beginner</SelectItem>
//                 <SelectItem value="intermediate">Intermediate</SelectItem>
//                 <SelectItem value="advanced">Advanced</SelectItem>
//               </SelectContent>
//             </Select>
//           </div>

//           {/* Style */}
//           <div className="space-y-2">
//             <Label htmlFor="style">Presentation Style *</Label>
//             <Select
//               value={formData.style}
//               onValueChange={(value: Style) => setFormData({ ...formData, style: value })}
//             >
//               <SelectTrigger className="bg-white/50">
//                 <SelectValue />
//               </SelectTrigger>
//               <SelectContent>
//                 <SelectItem value="concise">Concise</SelectItem>
//                 <SelectItem value="detailed">Detailed</SelectItem>
//                 <SelectItem value="exam-prep">Exam Preparation</SelectItem>
//               </SelectContent>
//             </Select>
//           </div>

//           {/* Submit Button */}
//           <Button
//             type="submit"
//             className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg hover:shadow-xl transition-all"
//             disabled={loading}
//           >
//             {loading ? "Generating..." : "Generate Plan"}
//           </Button>
//         </form>
//       </Card>

//       {/* API Response */}
//       {apiError && (
//         <Card className="p-6 bg-red-50 border-red-200">
//           <h3 className="text-lg font-semibold text-red-900 mb-2">Error</h3>
//           <p className="text-red-700">{apiError}</p>
//         </Card>
//       )}

//       {apiResponse && (
//         <Card className="p-6 bg-green-50 border-green-200">
//           <h3 className="text-lg font-semibold text-green-900 mb-2">Success!</h3>
//           <pre className="text-sm text-green-800 overflow-auto bg-white/50 p-4 rounded">
//             {JSON.stringify(apiResponse, null, 2)}
//           </pre>
//         </Card>
//       )}
//     </div>
//   );
// };

// export default GeneratorForm;
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card } from "@/components/ui/card";
import { Upload, Youtube, FileText } from "lucide-react";

type Level = "beginner" | "intermediate" | "advanced";
type Style = "concise" | "detailed" | "exam-prep";

interface GeneratorFormData {
  topic: string;
  description: string;
  youtubeLink: string;
  level: Level;
  style: Style;
  documents?: File[];
}

interface GeneratorFormProps {
  variant: "full" | "topic" | "youtube" | "document";
  onSubmit?: (data: GeneratorFormData) => void;
  isLoading?: boolean;
}

const GeneratorForm = ({ variant, onSubmit, isLoading = false }: GeneratorFormProps) => {
  const [formData, setFormData] = useState<GeneratorFormData>({
    topic: "",
    description: "",
    youtubeLink: "",
    level: "intermediate",
    style: "detailed",
  });
  const [apiLoading, setApiLoading] = useState(false);
  const [apiResponse, setApiResponse] = useState<any>(null);
  const [apiError, setApiError] = useState<string | null>(null);

  const handleSubmit = async () => {
    
  

    // Otherwise, call the API directly
    setApiLoading(true);
    setApiError(null);
    setApiResponse(null);

    try {
      const payload = {
        level: formData.level,
        style: formData.style,
        topics: formData.topic,
        description: formData.description,
        language: "en",
        model_name: "gpt-4" // You can make this configurable
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
        throw new Error(result.message || "Failed to generate plan");
      }

      setApiResponse(result);
    } catch (error) {
      setApiError(error instanceof Error ? error.message : "An error occurred");
    } finally {
      setApiLoading(false);
    }
  };

  const showYouTube = variant === "full" || variant === "youtube";
  const showDocuments = variant === "full" || variant === "document";
  const loading = isLoading || apiLoading;

  return (
    <div className="space-y-6">
      <Card className="p-8 bg-transparent border-slate-700/30">
        <div className="space-y-6">
          {/* Topic */}
          <div className="space-y-2">
            <Label htmlFor="topic" className="flex items-center gap-2">
              <FileText className="h-4 w-4 text-blue-600" />
              Topic Name *
            </Label>
            <Input
              id="topic"
              placeholder="Enter your topic..."
              value={formData.topic}
              onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
              required
              className="bg-slate-800/50 border-slate-700 text-white"
            />
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Topic Description</Label>
            <Textarea
              id="description"
              placeholder="Provide more details about your topic..."
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="bg-slate-800/50 border-slate-700 text-white"
            />
          </div>

          {/* YouTube Link */}
          {showYouTube && (
            <div className="space-y-2">
              <Label htmlFor="youtube" className="flex items-center gap-2">
                <Youtube className="h-4 w-4 text-blue-600" />
                YouTube Link {variant !== "youtube" && "(Optional)"}
              </Label>
              <Input
                id="youtube"
                type="url"
                placeholder="https://youtube.com/watch?v=..."
                value={formData.youtubeLink}
                onChange={(e) => setFormData({ ...formData, youtubeLink: e.target.value })}
                required={variant === "youtube"}
                className="bg-slate-800/50 border-slate-700 text-white"
              />
            </div>
          )}

          {/* Documents */}
          {showDocuments && (
            <div className="space-y-2">
              <Label htmlFor="documents" className="flex items-center gap-2">
                <Upload className="h-4 w-4 text-blue-600" />
                Upload Documents {variant !== "document" && "(Optional)"}
              </Label>
              <div className="border-2 border-dashed border-slate-700 rounded-lg p-6 text-center hover:border-blue-400 transition-colors bg-slate-800/30">
                <Upload className="h-8 w-8 text-slate-400 mx-auto mb-2" />
                <p className="text-sm text-slate-400 mb-2">
                  Click to upload or drag and drop
                </p>
                <Input
                  id="documents"
                  type="file"
                  multiple
                  className="hidden"
                  onChange={(e) => {
                    const files = Array.from(e.target.files || []);
                    setFormData({ ...formData, documents: files });
                  }}
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => document.getElementById("documents")?.click()}
                >
                  Select Files
                </Button>
                {formData.documents && formData.documents.length > 0 && (
                  <p className="text-xs text-slate-400 mt-2">
                    {formData.documents.length} file(s) selected
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Level */}
          <div className="space-y-2">
            <Label htmlFor="level">Difficulty Level *</Label>
            <Select
              value={formData.level}
              onValueChange={(value: Level) => setFormData({ ...formData, level: value })}
            >
              <SelectTrigger className="bg-slate-800/50 border-slate-700 text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="beginner">Beginner</SelectItem>
                <SelectItem value="intermediate">Intermediate</SelectItem>
                <SelectItem value="advanced">Advanced</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Style */}
          <div className="space-y-2">
            <Label htmlFor="style">Presentation Style *</Label>
            <Select
              value={formData.style}
              onValueChange={(value: Style) => setFormData({ ...formData, style: value })}
            >
              <SelectTrigger className="bg-slate-800/50 border-slate-700 text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="concise">Concise</SelectItem>
                <SelectItem value="detailed">Detailed</SelectItem>
                <SelectItem value="exam-prep">Exam Preparation</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Submit Button */}
          <Button
            type="button"
            onClick={handleSubmit}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg hover:shadow-xl transition-all"
            disabled={loading}
          >
            {loading ? "Generating..." : "Generate Plan"}
          </Button>
        </div>
      </Card>

      {/* API Response */}
      {apiError && (
        <Card className="p-6 bg-red-50 border-red-200">
          <h3 className="text-lg font-semibold text-red-900 mb-2">Error</h3>
          <p className="text-red-700">{apiError}</p>
        </Card>
      )}

      {apiResponse && (
        <Card className="p-6 bg-green-50 border-green-200">
          <h3 className="text-lg font-semibold text-green-900 mb-2">Success!</h3>
          <pre className="text-sm text-green-800 overflow-auto bg-slate-800/50 p-4 rounded border border-slate-700">
            {JSON.stringify(apiResponse, null, 2)}
          </pre>
        </Card>
      )}
    </div>
  );
};

export default GeneratorForm;