import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ThemeToggle } from "@/components/ThemeToggle";
import { BookOpen, Loader2, FileText, Edit, Download } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { apiService } from "@/services/api";
import { toast } from "sonner";

const TopicOnly = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [planLoading, setPlanLoading] = useState(false);
    const [downloadLoading, setDownloadLoading] = useState(false);
  const [formData, setFormData] = useState({
    topics: "",
    description: "",
    level: "beginner",
    style: "concise",
    language: "en",
  });
  const [planText, setPlanText] = useState("");
  const [userEdits, setUserEdits] = useState("");
  const [contentResult, setContentResult] = useState<any>(null);

  const handleGeneratePlan = async () => {
    if (!formData.topics) {
      toast.error("Please enter a topic");
      return;
    }

    setPlanLoading(true);
    try {
      const result = await apiService.generatePlan(formData);
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
      const result = await apiService.editPlan({
        plan_text: planText,
        user_edits: userEdits,
      });
      setPlanText(result.updated_plan || result.response || JSON.stringify(result));
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

    setLoading(true);
    try {
      const result = await apiService.generateTopicContent({
        plan_text: planText,
        level: formData.level,
        style: formData.style,
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

    const handleDownloadPPT = async () => {
      if (!contentResult?.ppt_filename) {
        toast.error("No PPT file available to download");
        return;
      }

      setDownloadLoading(true);
      try {
        await apiService.downloadPPT(contentResult.ppt_filename);
        toast.success("PPT downloaded successfully!");
      } catch (error) {
        toast.error("Failed to download PPT");
        console.error(error);
      } finally {
        setDownloadLoading(false);
      }
    };
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto px-4 py-4">
          <nav className="flex items-center justify-between">
            <button 
              onClick={() => navigate("/")}
              className="flex items-center gap-2 hover:opacity-80 transition-opacity"
            >
              <BookOpen className="h-8 w-8 text-primary" />
              <span className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">
                EduSlide AI
              </span>
            </button>
            <div className="flex items-center gap-4">
              <Button variant="outline" onClick={() => navigate("/select")}>
                Back
              </Button>
              <ThemeToggle />
            </div>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto space-y-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-4">Topic Only Generation</h1>
            <p className="text-lg text-muted-foreground">
              Generate comprehensive content from just a topic name
            </p>
          </div>

          {/* Form */}
          <Card className="p-6 bg-card">
            <div className="space-y-6">
              <div>
                <Label htmlFor="topic">Topic *</Label>
                <Input
                  id="topic"
                  placeholder="e.g., Photosynthesis, World War II, Quantum Mechanics"
                  value={formData.topics}
                  onChange={(e) => setFormData({ ...formData, topics: e.target.value })}
                />
              </div>

              <div>
                <Label htmlFor="description">Description (Optional)</Label>
                <Textarea
                  id="description"
                  placeholder="Provide additional context or specific areas to focus on..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={4}
                />
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label htmlFor="level">Level</Label>
                  <Select value={formData.level} onValueChange={(value) => setFormData({ ...formData, level: value })}>
                    <SelectTrigger id="level">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="beginner">Beginner</SelectItem>
                      <SelectItem value="intermediate">Intermediate</SelectItem>
                      <SelectItem value="advanced">Advanced</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="style">Style</Label>
                  <Select value={formData.style} onValueChange={(value) => setFormData({ ...formData, style: value })}>
                    <SelectTrigger id="style">
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
                className="w-full bg-gradient-primary hover:opacity-90"
                disabled={planLoading}
              >
                {planLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating Plan...
                  </>
                ) : (
                  <>
                    <FileText className="mr-2 h-4 w-4" />
                    Generate Plan
                  </>
                )}
              </Button>
            </div>
          </Card>

          {/* Plan Display & Edit */}
          {planText && (
            <Card className="p-6 bg-card space-y-6">
              <div>
                <h3 className="text-xl font-semibold mb-4">Generated Plan</h3>
                <div className="p-4 bg-muted rounded-lg whitespace-pre-wrap">
                  {planText}
                </div>
              </div>

              <div>
                <Label htmlFor="edits">Edit Plan (Optional)</Label>
                <Textarea
                  id="edits"
                  placeholder="Describe your changes or add additional requirements..."
                  value={userEdits}
                  onChange={(e) => setUserEdits(e.target.value)}
                  rows={4}
                />
                <Button 
                  onClick={handleEditPlan} 
                  className="mt-4 bg-accent hover:opacity-90"
                  disabled={planLoading || !userEdits.trim()}
                >
                  {planLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Updating Plan...
                    </>
                  ) : (
                    <>
                      <Edit className="mr-2 h-4 w-4" />
                      Update Plan
                    </>
                  )}
                </Button>
              </div>

              <Button 
                onClick={handleGenerateContent} 
                className="w-full bg-gradient-primary hover:opacity-90"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating Content...
                  </>
                ) : (
                  "Generate Content"
                )}
              </Button>
            </Card>
          )}

          {/* Content Result */}
          {contentResult && (
            <Card className="p-6 bg-card">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-semibold">Generated Content</h3>
                  {contentResult.ppt_filename && (
                    <Button
                      onClick={handleDownloadPPT}
                      disabled={downloadLoading}
                      variant="outline"
                    >
                      {downloadLoading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Downloading...
                        </>
                      ) : (
                        <>
                          <Download className="mr-2 h-4 w-4" />
                          Download PPT
                        </>
                      )}
                    </Button>
                  )}
                </div>
              <div className="p-4 bg-muted rounded-lg whitespace-pre-wrap">
                {JSON.stringify(contentResult, null, 2)}
              </div>
            </Card>
          )}
        </div>
      </main>
    </div>
  );
};

export default TopicOnly;
