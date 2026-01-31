import { GlassCard } from "@/components/ui/GlassCard";
import { FileText, Video, Link as LinkIcon, Upload, Layers, ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";

const SelectOption = () => {
  const navigate = useNavigate();

  const options = [
    {
      id: "topic",
      title: "Topic Only",
      description: "Generate comprehensive content from just a simple topic name.",
      icon: FileText,
      path: "/generate/topic",
      gradient: "from-blue-500 to-cyan-500",
    },
    {
      id: "youtube",
      title: "YouTube Content",
      description: "Convert any YouTube video into educational slides.",
      icon: Video,
      path: "/generate/youtube",
      gradient: "from-red-500 to-orange-500",
    },
    {
      id: "article",
      title: "Article Analysis",
      description: "Turn articles and blog posts into structured teaching material.",
      icon: LinkIcon,
      path: "/generate/article",
      gradient: "from-green-500 to-emerald-500",
    },
    {
      id: "document",
      title: "Document Upload",
      description: "Upload your PDFs or Docs to generate specific content.",
      icon: Upload,
      path: "/generate/document",
      gradient: "from-purple-500 to-pink-500",
    },
    {
      id: "combined",
      title: "Combined Sources",
      description: "The most powerful mode. Combine vectors for maximum depth.",
      icon: Layers,
      path: "/generate/combined",
      gradient: "from-amber-500 to-yellow-500",
    },
  ];

  return (
    <div className="space-y-12">
      <div className="text-center space-y-4 pt-8">
        <h1 className="text-4xl sm:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent">
          Choose Content Source
        </h1>
        <p className="text-lg text-muted-foreground max-w-xl mx-auto">
          Select how you would like to generate your presentation today.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 max-w-6xl mx-auto">
        {options.map((option) => {
          const Icon = option.icon;
          return (
            <GlassCard
              key={option.id}
              className="p-8 group cursor-pointer relative overflow-hidden"
              onClick={() => navigate(option.path)}
            >
              <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${option.gradient} opacity-10 blur-3xl rounded-full group-hover:opacity-20 transition-opacity`} />

              <div className="space-y-6 relative">
                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${option.gradient} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                  <Icon className="h-7 w-7 text-white" />
                </div>

                <div className="space-y-2">
                  <h3 className="text-2xl font-semibold group-hover:text-primary transition-colors">
                    {option.title}
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {option.description}
                  </p>
                </div>

                <div className="flex items-center text-sm font-medium text-primary opacity-0 group-hover:opacity-100 transition-all transform translate-x-[-10px] group-hover:translate-x-0">
                  Select Mode <ArrowRight className="ml-2 h-4 w-4" />
                </div>
              </div>
            </GlassCard>
          );
        })}
      </div>
    </div>
  );
};

export default SelectOption;
