import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { FileText, Youtube, Upload, Sparkles } from "lucide-react";
import Navbar from "@/components/Navbar";

const Landing = () => {
  const features = [
    {
      icon: FileText,
      title: "Topic-Based Generation",
      description: "Create comprehensive presentations from any topic with AI-powered content generation",
      link: "/generate/topic"
    },
    {
      icon: Youtube,
      title: "YouTube Integration",
      description: "Transform YouTube videos into structured presentations with core concepts",
      link: "/generate/youtube"
    },
    {
      icon: Upload,
      title: "Document Analysis",
      description: "Upload documents and let RAG MODEL extract key information for your slides",
      link: "/generate/document"
    },
    {
      icon: Sparkles,
      title: "Full Customization",
      description: "Combine all options with custom levels and styles for perfect presentations",
      link: "/generate/full"
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center space-y-6 animate-fade-in">
            <div className="inline-block">
              <span className="px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium border border-primary/20">
                Powered by NLC Concepts & RAG MODEL
              </span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight">
              <span className="bg-gradient-to-r from-primary via-cyan-light to-primary bg-clip-text text-transparent">
                Teaching Made Smarter
              </span>
            </h1>
            
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Transform your teaching materials into professional presentations with AI. 
              Generate, edit, and present with ease.
            </p>
            
            <div className="flex items-center justify-center gap-4 pt-4">
              <Link to="/generate/full">
                <Button size="lg" className="bg-gradient-accent shadow-glow hover:shadow-glow/50 transition-all">
                  <Sparkles className="mr-2 h-5 w-5" />
                  Start Creating
                </Button>
              </Link>
              <Button size="lg" variant="outline">
                Learn More
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Choose Your Creation Method</h2>
            <p className="text-muted-foreground">Multiple ways to generate perfect presentations</p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-6">
            {features.map((feature, index) => (
              <Link key={index} to={feature.link}>
                <Card className="p-6 bg-gradient-card border-border/40 hover:border-primary/40 transition-all hover:shadow-glow/20 cursor-pointer group h-full">
                  <div className="space-y-4">
                    <div className="p-3 rounded-lg bg-primary/10 w-fit group-hover:bg-gradient-accent transition-colors">
                      <feature.icon className="h-6 w-6 text-primary group-hover:text-primary-foreground" />
                    </div>
                    <h3 className="text-xl font-semibold group-hover:text-primary transition-colors">
                      {feature.title}
                    </h3>
                    <p className="text-muted-foreground">
                      {feature.description}
                    </p>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-4 bg-card/30">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">How It Works</h2>
            <p className="text-muted-foreground">Simple 3-step process</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: "1", title: "Input Content", desc: "Add your topic, links, or documents" },
              { step: "2", title: "Generate & Edit Plan", desc: "AI creates a plan, you refine it" },
              { step: "3", title: "Create Presentation", desc: "Generate your final PPT slides" }
            ].map((item) => (
              <div key={item.step} className="text-center space-y-4">
                <div className="w-16 h-16 rounded-full bg-gradient-accent flex items-center justify-center text-2xl font-bold mx-auto shadow-glow">
                  {item.step}
                </div>
                <h3 className="text-xl font-semibold">{item.title}</h3>
                <p className="text-muted-foreground">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-4xl">
          <Card className="p-12 bg-gradient-card border-primary/20 text-center space-y-6">
            <h2 className="text-4xl font-bold">Ready to Transform Your Teaching?</h2>
            <p className="text-xl text-muted-foreground">
              Join educators using AI to create better presentations
            </p>
            <Link to="/generate/full">
              <Button size="lg" className="bg-gradient-accent shadow-glow">
                <Sparkles className="mr-2 h-5 w-5" />
                Get Started Free
              </Button>
            </Link>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-border/40">
        <div className="container mx-auto max-w-6xl text-center text-muted-foreground">
          <p>© 2024 TeachAI. Powered by NLC & RAG MODEL</p>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
