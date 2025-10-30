import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ThemeToggle } from "@/components/ThemeToggle";
import { BookOpen, FileText, Video, Link as LinkIcon, Upload, Layers } from "lucide-react";
import { useNavigate } from "react-router-dom";

const SelectOption = () => {
  const navigate = useNavigate();

  const options = [
    {
      id: "topic",
      title: "Topic Only",
      description: "Generate content from just a topic name",
      icon: FileText,
      path: "/generate/topic",
    },
    {
      id: "youtube",
      title: "YouTube + Topic",
      description: "Combine YouTube videos with your topic",
      icon: Video,
      path: "/generate/youtube",
    },
    {
      id: "article",
      title: "Article + Topic",
      description: "Extract insights from online articles",
      icon: LinkIcon,
      path: "/generate/article",
    },
    {
      id: "document",
      title: "Document Upload",
      description: "Upload PDFs, DOCX, or images",
      icon: Upload,
      path: "/generate/document",
    },
    {
      id: "combined",
      title: "All Sources Combined",
      description: "Use multiple sources for comprehensive content",
      icon: Layers,
      path: "/generate/combined",
    },
  ];

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
            <ThemeToggle />
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4">
              Choose Your Content Source
            </h1>
            <p className="text-lg text-muted-foreground">
              Select how you'd like to generate your presentation content
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {options.map((option) => {
              const Icon = option.icon;
              return (
                <Card
                  key={option.id}
                  className="p-6 bg-card border-border hover:border-primary transition-all duration-300 hover:shadow-lg hover:shadow-primary/20 cursor-pointer group"
                  onClick={() => navigate(option.path)}
                >
                  <div className="space-y-4">
                    <div className="h-14 w-14 rounded-lg bg-gradient-primary flex items-center justify-center group-hover:scale-110 transition-transform">
                      <Icon className="h-7 w-7 text-primary-foreground" />
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold mb-2">{option.title}</h3>
                      <p className="text-muted-foreground">{option.description}</p>
                    </div>
                    <Button className="w-full bg-gradient-primary hover:opacity-90 transition-opacity">
                      Select
                    </Button>
                  </div>
                </Card>
              );
            })}
          </div>
        </div>
      </main>
    </div>
  );
};

export default SelectOption;
