import { useState } from "react";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/GlassCard";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2, FileText, Edit, Plus, X, Upload, Download, ChevronRight, Check, Sparkles } from "lucide-react";

import { useNavigate } from "react-router-dom";
import { apiService } from "@/services/api";
import { toast } from "sonner";
import { PlanViewer } from "@/components/PlanViewer";

const Document = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [planLoading, setPlanLoading] = useState(false);
  const [formData, setFormData] = useState({
    file: null as File | null,
    topics: [""],
    description: "",
    level: "beginner",
    style: "concise",
    language: "en",
  });
  const [planText, setPlanText] = useState("");
  const [userEdits, setUserEdits] = useState("");
  const [contentResult, setContentResult] = useState<any>(null);
  const [downloadLoading, setDownloadLoading] = useState(false);


  const addTopic = () => {
    setFormData({ ...formData, topics: [...formData.topics, ""] });
  };

  const removeTopic = (index: number) => {
    const newTopics = formData.topics.filter((_, i) => i !== index);
    setFormData({ ...formData, topics: newTopics });
  };

  const updateTopic = (index: number, value: string) => {
    const newTopics = [...formData.topics];
    newTopics[index] = value;
    setFormData({ ...formData, topics: newTopics });
  };
  const handleDownloadPPT = async () => {
    if (!contentResult?.ppt_filename) {
      toast.error("No PPT file available to download");
      return;
    }

    setDownloadLoading(true);
    try {
      await apiService.downloadYoutubePPT(contentResult.ppt_filename);
      toast.success("PPT downloaded successfully!");
    } catch (error) {
      toast.error("Failed to download PPT");
      console.error(error);
    } finally {
      setDownloadLoading(false);
    }
  };
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFormData({ ...formData, file: e.target.files[0] });
    }
  };

  const handleGeneratePlan = async () => {
    const validTopics = formData.topics.filter(t => t.trim());
    if (!validTopics.length) {
      toast.error("Please enter at least one topic");
      return;
    }

    setPlanLoading(true);
    try {
      const result = await apiService.generatePlan({
        topics: validTopics.join(", "),
        description: formData.description,
        level: formData.level,
        style: formData.style,
        language: formData.language,
      });
      setPlanText(result.plan || result.response || JSON.stringify(result));
      toast.success("Plan generated successfully!");
    } catch (error) {
      toast.error("Failed to generate plan");
      console.error(error);
    } finally {
      setPlanLoading(false);
    }
  };

  const handleEditPlan = async () => {
    if (!userEdits.trim()) {
      toast.error("Please enter your edits");
      return;
    }

    setPlanLoading(true);
    try {
      const validTopics = formData.topics.filter(t => t.trim()).join(", ");
      const result = await apiService.editPlan({
        ...formData,
        // Override topics to match API (string not array)
        topics: validTopics,
        user_edits: userEdits,
      });
      setPlanText(result.plan || result.response || JSON.stringify(result));
      setUserEdits("");
      toast.success("Plan updated successfully!");
    } catch (error) {
      toast.error("Failed to edit plan");
      console.error(error);
    } finally {
      setPlanLoading(false);
    }
  };

  const handleGenerateContent = async () => {
    if (!planText) {
      toast.error("Please generate a plan first");
      return;
    }
    if (!formData.file) {
      toast.error("Please upload a document");
      return;
    }

    setLoading(true);
    try {
      const validTopics = formData.topics.filter(t => t.trim());
      const result = await apiService.generateFileContent({
        file: formData.file,
        plan_text: planText,
        topics: validTopics,
        level: formData.level,
        style: formData.style,
        language: formData.language,
      });
      setContentResult(result);
      toast.success("Content generated successfully!");
    } catch (error) {
      toast.error("Failed to generate content");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fade-in pb-12 pt-6">
      {/* Page Header */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => navigate("/select")}
          className="rounded-full hover:bg-primary/10 hover:text-primary transition-colors"
        >
          <ChevronRight className="h-6 w-6 rotate-180" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
            Document Upload
          </h1>
          <p className="text-muted-foreground">
            Generate content from PDF, DOCX, TXT, or Images.
          </p>
        </div>
      </div>

      <div className="grid gap-8 lg:grid-cols-[1fr,1.5fr]">
        {/* Left Column: Form */}
        <div className="space-y-6">
          <GlassCard className="p-6 space-y-6 border-l-4 border-l-primary">
            <h3 className="text-xl font-semibold flex items-center gap-2">
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-white text-xs">1</span>
              Upload & Config
            </h3>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="file">Upload Document *</Label>
                <div className="relative group">
                  <Input
                    id="file"
                    type="file"
                    accept=".pdf,.docx,.txt,.png,.jpg,.jpeg,.tiff"
                    onChange={handleFileChange}
                    className="cursor-pointer bg-white/50 dark:bg-black/20 file:bg-primary/10 file:text-primary file:border-0 file:rounded-md file:px-2 file:py-1 file:mr-2 file:font-semibold hover:file:bg-primary/20 transition-all"
                  />
                </div>
                {formData.file && (
                  <p className="text-sm text-green-600 flex items-center gap-2 mt-1">
                    <Check className="h-3 w-3" />
                    {formData.file.name}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label>Topics *</Label>
                <div className="space-y-2">
                  {formData.topics.map((topic, index) => (
                    <div key={index} className="flex gap-2">
                      <Input
                        placeholder="Enter a topic"
                        value={topic}
                        onChange={(e) => updateTopic(index, e.target.value)}
                        className="bg-white/50 dark:bg-black/20"
                      />
                      {formData.topics.length > 1 && (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => removeTopic(index)}
                          className="hover:text-destructive"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  ))}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={addTopic}
                    className="w-full border-dashed"
                  >
                    <Plus className="mr-2 h-4 w-4" />
                    Add Topic
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Context (Optional)</Label>
                <Textarea
                  id="description"
                  placeholder="Additional context..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                  className="bg-white/50 dark:bg-black/20 resize-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Level</Label>
                  <Select value={formData.level} onValueChange={(value) => setFormData({ ...formData, level: value })}>
                    <SelectTrigger className="bg-white/50 dark:bg-black/20">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="beginner">Beginner</SelectItem>
                      <SelectItem value="intermediate">Intermediate</SelectItem>
                      <SelectItem value="advanced">Advanced</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Style</Label>
                  <Select value={formData.style} onValueChange={(value) => setFormData({ ...formData, style: value })}>
                    <SelectTrigger className="bg-white/50 dark:bg-black/20">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="concise">Concise</SelectItem>
                      <SelectItem value="detailed">Detailed</SelectItem>
                      <SelectItem value="exam-prep">Exam Prep</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Button
                onClick={handleGeneratePlan}
                className="w-full bg-primary hover:bg-primary/90 shadow-lg shadow-primary/20"
                disabled={planLoading}
              >
                {planLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating Plan...
                  </>
                ) : (
                  <>
                    <Sparkles className="mr-2 h-4 w-4" />
                    Generate Plan
                  </>
                )}
              </Button>
            </div>
          </GlassCard>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {!planText && !contentResult && (
            <GlassCard className="h-full min-h-[400px] flex flex-col items-center justify-center text-center p-8 border-dashed border-2 border-white/20 bg-white/5">
              <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
                <Upload className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Upload & Generate</h3>
              <p className="text-muted-foreground max-w-sm">
                Upload your documents on the left to extract insights and generate slides.
              </p>
            </GlassCard>
          )}

          {planText && (
            <GlassCard className="p-6 space-y-6 animate-in slide-in-from-bottom-4 duration-500">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-semibold flex items-center gap-2">
                  <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-white text-xs">2</span>
                  Review Plan
                </h3>
                <div className="text-xs font-mono bg-primary/10 text-primary px-2 py-1 rounded">PLANNING PHASE</div>
              </div>

              <div className="p-4 bg-muted/50 rounded-lg border border-white/10 max-h-[600px] overflow-y-auto">
                <PlanViewer planData={planText} />
              </div>

              <div className="space-y-4 pt-4 border-t border-white/10">
                <div className="space-y-2">
                  <Label htmlFor="edits" className="text-xs uppercase tracking-wider text-muted-foreground">Refine Plan (Optional)</Label>
                  <div className="flex gap-2">
                    <Textarea
                      id="edits"
                      placeholder="e.g., Add more focus on financial aspects..."
                      value={userEdits}
                      onChange={(e) => setUserEdits(e.target.value)}
                      rows={1}
                      className="bg-white/50 dark:bg-black/20 resize-none min-h-[40px]"
                    />
                    <Button
                      onClick={handleEditPlan}
                      variant="outline"
                      size="icon"
                      className="shrink-0"
                      disabled={planLoading || !userEdits.trim()}
                    >
                      {planLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Edit className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>

                <Button
                  onClick={handleGenerateContent}
                  className="w-full bg-gradient-to-r from-emerald-500 to-green-600 hover:opacity-90 shadow-lg shadow-emerald-500/20"
                  disabled={loading}
                  size="lg"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Creating Slides...
                    </>
                  ) : (
                    <>
                      <ChevronRight className="mr-2 h-5 w-5" />
                      Approve & Generate Content
                    </>
                  )}
                </Button>
              </div>
            </GlassCard>
          )}

          {contentResult && (
            <GlassCard className="p-6 space-y-6 border-green-500/20 bg-green-500/5 animate-in zoom-in-95 duration-500">
              <div className="text-center space-y-2">
                <div className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-2">
                  <Check className="h-8 w-8 text-green-500" />
                </div>
                <h3 className="text-2xl font-bold text-green-500">Generation Complete!</h3>
                <p className="text-muted-foreground">Your presentation is ready for download.</p>
              </div>

              {contentResult.ppt_filename && (
                <Button
                  onClick={handleDownloadPPT}
                  disabled={downloadLoading}
                  className="w-full h-12 text-lg bg-green-600 hover:bg-green-700 shadow-xl shadow-green-600/20"
                >
                  {downloadLoading ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Downloading...
                    </>
                  ) : (
                    <>
                      <Download className="mr-2 h-5 w-5" />
                      Download PowerPoint (.pptx)
                    </>
                  )}
                </Button>
              )}
            </GlassCard>
          )}

        </div>
      </div>

    </div>
  );
};

export default Document;
