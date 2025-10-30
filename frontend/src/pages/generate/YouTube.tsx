import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { BookOpen, Loader2, FileText, Edit, Plus, X, Download } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ThemeToggle } from "@/components/ThemeToggle";
import { useNavigate } from "react-router-dom";
import { apiService } from "@/services/api";
import { toast } from "sonner";

const YouTube = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [planLoading, setPlanLoading] = useState(false);
  const [downloadLoading, setDownloadLoading] = useState(false);

  const [formData, setFormData] = useState({
    video: "",
    topics: [""],
    description: "",
    level: "beginner",
    style: "concise",
    language: "en",
  });
  const [planText, setPlanText] = useState("");
  const [userEdits, setUserEdits] = useState("");
  const [contentResult, setContentResult] = useState<any>(null);

  const addTopic = () => {
    setFormData({ ...formData, topics: [...formData.topics, ""] });
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

  const removeTopic = (index: number) => {
    const newTopics = formData.topics.filter((_, i) => i !== index);
    setFormData({ ...formData, topics: newTopics });
  };

  const updateTopic = (index: number, value: string) => {
    const newTopics = [...formData.topics];
    newTopics[index] = value;
    setFormData({ ...formData, topics: newTopics });
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
    if (!formData.video) {
      toast.error("Please enter a YouTube URL");
      return;
    }

    setLoading(true);
    try {
      const validTopics = formData.topics.filter(t => t.trim());
      const result = await apiService.generateYTContent({
        video: formData.video,
        plan_text: planText,
        level: formData.level,
        style: formData.style,
        topics: validTopics,
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
    <div className="min-h-screen bg-background">
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

      <main className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto space-y-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-4">YouTube + Topic</h1>
            <p className="text-lg text-muted-foreground">
              Generate content from YouTube videos and topics
            </p>
          </div>

          <Card className="p-6 bg-card">
            <div className="space-y-6">
              <div>
                <Label htmlFor="video">YouTube URL *</Label>
                <Input
                  id="video"
                  placeholder="https://www.youtube.com/watch?v=..."
                  value={formData.video}
                  onChange={(e) => setFormData({ ...formData, video: e.target.value })}
                />
              </div>

              <div>
                <Label>Topics *</Label>
                <div className="space-y-2">
                  {formData.topics.map((topic, index) => (
                    <div key={index} className="flex gap-2">
                      <Input
                        placeholder="Enter a topic"
                        value={topic}
                        onChange={(e) => updateTopic(index, e.target.value)}
                      />
                      {formData.topics.length > 1 && (
                        <Button
                          variant="outline"
                          size="icon"
                          onClick={() => removeTopic(index)}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  ))}
                  <Button
                    variant="outline"
                    onClick={addTopic}
                    className="w-full"
                  >
                    <Plus className="mr-2 h-4 w-4" />
                    Add Topic
                  </Button>
                </div>
              </div>

              <div>
                <Label htmlFor="description">Description (Optional)</Label>
                <Textarea
                  id="description"
                  placeholder="Additional context..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={4}
                />
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label>Level</Label>
                  <Select value={formData.level} onValueChange={(value) => setFormData({ ...formData, level: value })}>
                    <SelectTrigger>
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
                  <Label>Style</Label>
                  <Select value={formData.style} onValueChange={(value) => setFormData({ ...formData, style: value })}>
                    <SelectTrigger>
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

          {planText && (
            <Card className="p-6 bg-card space-y-6">
              <div>
                <h3 className="text-xl font-semibold mb-4">Generated Plan</h3>
                <div className="p-4 bg-muted rounded-lg">
                  {(() => {
                    let plan;
                    try {
                      plan = typeof planText === "string" ? JSON.parse(planText) : planText;
                    } catch {
                      return <pre className="whitespace-pre-wrap text-sm">{planText}</pre>;
                    }
                    if (!plan || typeof plan !== "object") return <pre>{planText}</pre>;
                    return (
                      <div className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div>
                            <span className="font-semibold">Level:</span> {plan.level}
                          </div>
                          <div>
                            <span className="font-semibold">Style:</span> {plan.style}
                          </div>
                          <div>
                            <span className="font-semibold">Language:</span> {plan.language}
                          </div>
                        </div>
                        <div>
                          <span className="font-semibold">Topics:</span>
                          <ul className="list-disc ml-6">
                            {plan.topics?.map((t: string, i: number) => (
                              <li key={i}>{t}</li>
                            ))}
                          </ul>
                        </div>
                        {plan.planner_notes && (
                          <div>
                            <span className="font-semibold">Planner Notes:</span>
                            <div className="bg-background rounded p-2 mt-1 text-sm">{plan.planner_notes}</div>
                          </div>
                        )}
                        {plan.overall_objectives && (
                          <div>
                            <span className="font-semibold">Overall Objectives:</span>
                            <ul className="list-disc ml-6">
                              {plan.overall_objectives.map((obj: string, i: number) => (
                                <li key={i}>{obj}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {plan.subtopics && plan.subtopics.length > 0 && (
                          <div>
                            <span className="font-semibold">Subtopics:</span>
                            <div className="space-y-4 mt-2">
                              {plan.subtopics.map((sub: any, i: number) => (
                                <Card key={i} className="p-4 bg-background border">
                                  <div className="font-semibold text-lg mb-2">{sub.title}</div>
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-2">
                                    <div>
                                      <span className="font-semibold">Weight:</span> {sub.weight}
                                    </div>
                                    <div>
                                      <span className="font-semibold">Estimated Time:</span> {sub.estimated_time_minutes} min
                                    </div>
                                  </div>
                                  {sub.learning_outcomes && (
                                    <div>
                                      <span className="font-semibold">Learning Outcomes:</span>
                                      <ul className="list-disc ml-6">
                                        {sub.learning_outcomes.map((lo: string, idx: number) => (
                                          <li key={idx}>{lo}</li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                  {sub.key_terms && (
                                    <div>
                                      <span className="font-semibold">Key Terms:</span>
                                      <ul className="list-disc ml-6">
                                        {sub.key_terms.map((kt: string, idx: number) => (
                                          <li key={idx}>{kt}</li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                  {sub.suggested_examples && (
                                    <div>
                                      <span className="font-semibold">Suggested Examples:</span>
                                      <ul className="list-disc ml-6">
                                        {sub.suggested_examples.map((ex: string, idx: number) => (
                                          <li key={idx}>{ex}</li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                  <div>
                                    <span className="font-semibold">Suggested Questions:</span> {sub.suggested_questions}
                                  </div>
                                </Card>
                              ))}
                            </div>
                          </div>
                        )}
                        {plan.assessment_strategy && (
                          <div>
                            <span className="font-semibold">Assessment Strategy:</span>
                            <div className="mt-2">
                              <div>
                                <span className="font-semibold">Format:</span>
                                <ul className="list-disc ml-6">
                                  {plan.assessment_strategy.format?.map((fmt: string, i: number) => (
                                    <li key={i}>{fmt}</li>
                                  ))}
                                </ul>
                              </div>
                              {plan.assessment_strategy.notes && (
                                <div className="mt-1">
                                  <span className="font-semibold">Notes:</span> {plan.assessment_strategy.notes}
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })()}
                </div>
              </div>

              <div>
                <Label htmlFor="edits">Edit Plan (Optional)</Label>
                <Textarea
                  id="edits"
                  placeholder="Describe your changes..."
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

export default YouTube;
