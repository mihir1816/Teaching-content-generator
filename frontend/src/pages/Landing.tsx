import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ThemeToggle } from "@/components/ThemeToggle";
import { BookOpen, Sparkles, Zap, FileText, Video, Link as LinkIcon } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Landing = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-hero">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <nav className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BookOpen className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              EduSlide AI
            </span>
          </div>
          <ThemeToggle />
        </nav>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="mx-auto max-w-4xl space-y-8">
          <div className="space-y-4">
            <h1 className="text-5xl font-bold tracking-tight sm:text-6xl lg:text-7xl">
              Transform Teaching with
              <span className="block bg-gradient-primary bg-clip-text text-transparent">
                AI-Powered Presentations
              </span>
            </h1>
            <p className="mx-auto max-w-2xl text-lg text-muted-foreground sm:text-xl">
              Generate comprehensive PowerPoint presentations using NLC concepts and RAG models. 
              Create engaging content from topics, videos, articles, or documents.
            </p>
          </div>
          
          <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
            <Button
              size="lg"
              className="bg-gradient-primary hover:opacity-90 transition-opacity text-lg px-8"
              onClick={() => navigate("/select")}
            >
              <Sparkles className="mr-2 h-5 w-5" />
              Get Started
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="text-lg px-8"
            >
              Learn More
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">
            Multiple Ways to Generate Content
          </h2>
          <p className="text-muted-foreground text-lg">
            Choose the input method that works best for your teaching needs
          </p>
        </div>
        
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card className="p-6 bg-card border-border hover:border-primary transition-all duration-300 hover:shadow-lg hover:shadow-primary/20">
            <div className="space-y-4">
              <div className="h-12 w-12 rounded-lg bg-gradient-primary flex items-center justify-center">
                <FileText className="h-6 w-6 text-primary-foreground" />
              </div>
              <h3 className="text-xl font-semibold">Topic Only</h3>
              <p className="text-muted-foreground">
                Enter just a topic and let AI generate comprehensive content
              </p>
            </div>
          </Card>

          <Card className="p-6 bg-card border-border hover:border-primary transition-all duration-300 hover:shadow-lg hover:shadow-primary/20">
            <div className="space-y-4">
              <div className="h-12 w-12 rounded-lg bg-gradient-primary flex items-center justify-center">
                <Video className="h-6 w-6 text-primary-foreground" />
              </div>
              <h3 className="text-xl font-semibold">YouTube + Topic</h3>
              <p className="text-muted-foreground">
                Combine video content with your topic for rich presentations
              </p>
            </div>
          </Card>

          <Card className="p-6 bg-card border-border hover:border-primary transition-all duration-300 hover:shadow-lg hover:shadow-primary/20">
            <div className="space-y-4">
              <div className="h-12 w-12 rounded-lg bg-gradient-primary flex items-center justify-center">
                <LinkIcon className="h-6 w-6 text-primary-foreground" />
              </div>
              <h3 className="text-xl font-semibold">Article + Topic</h3>
              <p className="text-muted-foreground">
                Extract insights from articles to enhance your slides
              </p>
            </div>
          </Card>

          <Card className="p-6 bg-card border-border hover:border-primary transition-all duration-300 hover:shadow-lg hover:shadow-primary/20">
            <div className="space-y-4">
              <div className="h-12 w-12 rounded-lg bg-gradient-primary flex items-center justify-center">
                <FileText className="h-6 w-6 text-primary-foreground" />
              </div>
              <h3 className="text-xl font-semibold">Document Upload</h3>
              <p className="text-muted-foreground">
                Upload PDFs, DOCX, or images to generate targeted content
              </p>
            </div>
          </Card>

          <Card className="p-6 bg-card border-border hover:border-primary transition-all duration-300 hover:shadow-lg hover:shadow-primary/20">
            <div className="space-y-4">
              <div className="h-12 w-12 rounded-lg bg-gradient-primary flex items-center justify-center">
                <Zap className="h-6 w-6 text-primary-foreground" />
              </div>
              <h3 className="text-xl font-semibold">Combined Approach</h3>
              <p className="text-muted-foreground">
                Use all sources together for maximum comprehensive content
              </p>
            </div>
          </Card>

          <Card className="p-6 bg-card border-border hover:border-accent transition-all duration-300 hover:shadow-lg hover:shadow-accent/20">
            <div className="space-y-4">
              <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-accent to-primary flex items-center justify-center">
                <Sparkles className="h-6 w-6 text-primary-foreground" />
              </div>
              <h3 className="text-xl font-semibold">AI-Powered</h3>
              <p className="text-muted-foreground">
                Advanced NLC and RAG models ensure quality content generation
              </p>
            </div>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20">
        <Card className="p-12 text-center bg-gradient-dark border-0">
          <div className="mx-auto max-w-2xl space-y-6">
            <h2 className="text-3xl font-bold text-primary-foreground">
              Ready to Transform Your Teaching?
            </h2>
            <p className="text-lg text-primary-foreground/80">
              Start creating AI-powered presentations in minutes
            </p>
            <Button
              size="lg"
              className="bg-accent hover:opacity-90 transition-opacity text-lg px-8"
              onClick={() => navigate("/select")}
            >
              Start Creating Now
            </Button>
          </div>
        </Card>
      </section>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-8 text-center text-muted-foreground">
        <p>© 2024 EduSlide AI. Powered by NLC & RAG Technology.</p>
      </footer>
    </div>
  );
};

export default Landing;
