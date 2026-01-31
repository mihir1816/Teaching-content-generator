import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/GlassCard";
import { Sparkles, FileText, Video, Link as LinkIcon, Upload, ArrowRight, CheckCircle2 } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Landing = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col gap-12 sm:gap-24">
      {/* Hero Section */}
      <section className="relative text-center space-y-8 pt-12 sm:pt-24 pb-8">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-primary/20 blur-[120px] rounded-full -z-10" />

        <div className="space-y-4 animate-fade-in">
          <div className="inline-flex items-center rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-sm text-primary backdrop-blur-sm">
            <span className="flex h-2 w-2 rounded-full bg-primary mr-2 animate-pulse" />
            New Feature: Multi-source Generation
          </div>

          <h1 className="text-5xl sm:text-7xl font-bold tracking-tight max-w-[900px] mx-auto leading-tight">
            Transform Ideas into <br />
            <span className="text-gradient">Stunning Presentations</span>
          </h1>

          <p className="mx-auto max-w-2xl text-lg sm:text-xl text-muted-foreground leading-relaxed">
            Harness the power of AI to generate comprehensive, educational slide decks from topics, videos, articles, or documents in seconds.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <Button
            size="lg"
            className="h-14 px-8 text-lg rounded-full bg-gradient-to-r from-primary to-accent hover:opacity-90 transition-all shadow-lg hover:shadow-primary/25 hover:-translate-y-0.5"
            onClick={() => navigate("/select")}
          >
            <Sparkles className="mr-2 h-5 w-5" />
            Start Creating Free
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="h-14 px-8 text-lg rounded-full border-primary/20 hover:bg-primary/5 backdrop-blur-sm"
          >
            View Examples
          </Button>
        </div>
      </section>

      {/* Stats / Social Proof */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto w-full">
        {[
          { label: "Slides Generated", value: "10k+" },
          { label: "active Users", value: "5k+" },
          { label: "Time Saved", value: "50k+ hrs" },
          { label: "Rating", value: "4.9/5" },
        ].map((stat, i) => (
          <div key={i} className="text-center space-y-1">
            <h3 className="text-3xl font-bold text-foreground">{stat.value}</h3>
            <p className="text-sm text-muted-foreground uppercase tracking-wider">{stat.label}</p>
          </div>
        ))}
      </section>

      {/* Features Grid */}
      <section className="space-y-12">
        <div className="text-center space-y-4">
          <h2 className="text-3xl sm:text-4xl font-bold">Everything you need to teach</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Our advanced RAG models analyze your content to extract key insights and structure them perfectly for presentation.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[
            {
              icon: FileText,
              title: "Topic to Slides",
              desc: "Just enter a subject and let our AI research and structure the entire presentation for you.",
              gradient: "from-blue-500 to-cyan-500"
            },
            {
              icon: Video,
              title: "Video to slides",
              desc: "Paste a YouTube URL and we'll extract the transcript, key points, and create visual slides.",
              gradient: "from-red-500 to-orange-500"
            },
            {
              icon: LinkIcon,
              title: "Article to Slides",
              desc: "Turn any blog post or news article into a teaching resource in seconds.",
              gradient: "from-green-500 to-emerald-500"
            },
            {
              icon: Upload,
              title: "Document Analysis",
              desc: "Upload PDFs or Word docs. We read them and summarize them into slide format.",
              gradient: "from-purple-500 to-pink-500"
            },
            {
              icon: CheckCircle2,
              title: "Smart Formatting",
              desc: "Auto-layout, bullet points, and image suggestions for professional looking slides.",
              gradient: "from-amber-500 to-yellow-500"
            },
            {
              icon: Sparkles,
              title: "Export to PPTX",
              desc: "Download fully editable PowerPoint files compatible with Microsoft Office and Google Slides.",
              gradient: "from-indigo-500 to-violet-500"
            },
          ].map((feature, i) => (
            <GlassCard key={i} className="p-8 space-y-4 group">
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                <feature.icon className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold">{feature.title}</h3>
              <p className="text-muted-foreground leading-relaxed">
                {feature.desc}
              </p>
            </GlassCard>
          ))}
        </div>
      </section>

      {/* Simple CTA */}
      <GlassCard className="p-12 text-center space-y-6 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-r from-primary/10 to-accent/10 -z-10" />
        <h2 className="text-3xl sm:text-4xl font-bold">Ready to streamline your workflow?</h2>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Join thousands of educators and creators who are saving hours every week.
        </p>
        <Button
          size="lg"
          className="h-12 px-8 rounded-full bg-primary hover:bg-primary/90 text-lg shadow-xl shadow-primary/20"
          onClick={() => navigate("/select")}
        >
          Get Started Now <ArrowRight className="ml-2 h-5 w-5" />
        </Button>
      </GlassCard>
    </div>
  );
};

export default Landing;

