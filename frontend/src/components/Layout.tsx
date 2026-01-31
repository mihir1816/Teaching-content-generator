import { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import { BookOpen, Github, MessageSquare } from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";
import AnimatedBackground from "./ui/AnimatedBackground";
import { Button } from "./ui/button";

interface LayoutProps {
    children: ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
    const location = useLocation();
    const isHome = location.pathname === "/";

    return (
        <div className="relative min-h-screen flex flex-col font-sans text-foreground">
            <AnimatedBackground />

            {/* Navbar */}
            <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-white/10 dark:bg-black/10 backdrop-blur-md supports-[backdrop-filter]:bg-white/5">
                <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                    <Link to="/" className="flex items-center gap-2 group">
                        <div className="bg-gradient-to-tr from-primary to-accent p-2 rounded-lg group-hover:scale-110 transition-transform duration-300 shadow-lg shadow-primary/25">
                            <BookOpen className="h-5 w-5 text-white" />
                        </div>
                        <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/70 dark:from-white dark:to-white/70">
                            EduSlide<span className="text-primary">AI</span>
                        </span>
                    </Link>

                    <nav className="hidden md:flex items-center gap-6">
                        <Link
                            to="/"
                            className={`text-sm font-medium transition-colors hover:text-primary ${isHome ? 'text-primary' : 'text-muted-foreground'}`}
                        >
                            Home
                        </Link>
                        <Link
                            to="/select"
                            className={`text-sm font-medium transition-colors hover:text-primary ${location.pathname.startsWith('/select') || location.pathname.startsWith('/generate') ? 'text-primary' : 'text-muted-foreground'}`}
                        >
                            Create
                        </Link>
                        <a href="#" className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary">
                            Templates
                        </a>
                        <a href="#" className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary">
                            Pricing
                        </a>
                    </nav>

                    <div className="flex items-center gap-4">
                        <div className="hidden sm:flex items-center gap-2">
                            <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-primary">
                                <Github className="h-5 w-5" />
                            </Button>
                            <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-primary">
                                <MessageSquare className="h-5 w-5" />
                            </Button>
                        </div>
                        <div className="h-6 w-px bg-white/10 hidden sm:block" />
                        <ThemeToggle />
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 container mx-auto px-4 py-8 relative z-10 w-full max-w-7xl animate-fade-in">
                {children}
            </main>

            {/* Footer */}
            <footer className="border-t border-white/10 bg-black/5 backdrop-blur-sm mt-auto">
                <div className="container mx-auto px-4 py-8">
                    <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                        <p className="text-sm text-muted-foreground text-center md:text-left">
                            © 2024 EduSlide AI. Powered by Advanced NLC & RAG Technology.
                        </p>
                        <div className="flex items-center gap-6 text-sm text-muted-foreground">
                            <a href="#" className="hover:text-primary transition-colors">Privacy</a>
                            <a href="#" className="hover:text-primary transition-colors">Terms</a>
                            <a href="#" className="hover:text-primary transition-colors">Contact</a>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default Layout;
