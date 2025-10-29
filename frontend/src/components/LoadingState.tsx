import { Loader2, Sparkles, Brain, Zap } from "lucide-react";

interface LoadingStateProps {
  message?: string;
}

const LoadingState = ({ message = "Generating with AI..." }: LoadingStateProps) => {
  return (
    <div className="flex flex-col items-center justify-center py-20 space-y-6">
      <div className="relative">
        <div className="absolute inset-0 animate-ping">
          <div className="h-20 w-20 rounded-full bg-primary/20"></div>
        </div>
        <div className="relative h-20 w-20 rounded-full bg-gradient-accent flex items-center justify-center shadow-glow">
          <Sparkles className="h-10 w-10 text-primary-foreground animate-pulse" />
        </div>
      </div>
      
      <div className="text-center space-y-2">
        <h3 className="text-xl font-semibold">{message}</h3>
        <p className="text-muted-foreground">This may take a moment...</p>
      </div>
      
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 text-sm text-muted-foreground animate-pulse">
          <Brain className="h-4 w-4 text-primary" />
          <span>Analyzing</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground animate-pulse delay-100">
          <Zap className="h-4 w-4 text-primary" />
          <span>Processing</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground animate-pulse delay-200">
          <Sparkles className="h-4 w-4 text-primary" />
          <span>Creating</span>
        </div>
      </div>
      
      <div className="w-64 h-1 bg-secondary rounded-full overflow-hidden">
        <div className="h-full bg-gradient-accent animate-shimmer bg-[length:200%_100%]"></div>
      </div>
    </div>
  );
};

export default LoadingState;
