import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { GlassCard } from "@/components/ui/GlassCard";
import {
    BookOpen,
    Clock,
    Target,
    Lightbulb,
    HelpCircle,
    GraduationCap,
    Brain,
    CheckCircle2,
    List
} from "lucide-react";

interface PlanViewerProps {
    planData: any;
}

export const PlanViewer = ({ planData }: PlanViewerProps) => {
    // Handle different data structures (direct object or wrapped in data/success)
    const plan = typeof planData === 'string'
        ? JSON.parse(planData)
        : planData;

    // Drill down if wrapped in data.data or similar
    const actualPlan = plan?.data || plan?.plan || plan;

    if (!actualPlan) {
        return (
            <div className="p-4 text-center text-muted-foreground">
                No plan data available to display.
            </div>
        );
    }

    // Helper to safely render arrays
    const renderList = (items: any[]) => {
        if (!items || !Array.isArray(items)) return null;
        return items.map((item, idx) => (
            <li key={idx} className="text-sm text-muted-foreground/90 mb-1">
                {item}
            </li>
        ));
    };

    // Determine objectives (handle both naming conventions)
    const objectives = actualPlan.overall_objectives || actualPlan.objectives;

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            {/* High Level Stats - Only show if available */}
            {(actualPlan.level || actualPlan.style || actualPlan.language) && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <GlassCard className="p-3 flex flex-col items-center justify-center bg-primary/5 border-primary/20">
                        <span className="text-xs text-muted-foreground uppercase tracking-wider">Level</span>
                        <span className="font-bold capitalize text-primary">{actualPlan.level || 'N/A'}</span>
                    </GlassCard>
                    <GlassCard className="p-3 flex flex-col items-center justify-center bg-blue-500/5 border-blue-500/20">
                        <span className="text-xs text-muted-foreground uppercase tracking-wider">Style</span>
                        <span className="font-bold capitalize text-blue-500">{actualPlan.style || 'N/A'}</span>
                    </GlassCard>
                    <GlassCard className="p-3 flex flex-col items-center justify-center bg-emerald-500/5 border-emerald-500/20">
                        <span className="text-xs text-muted-foreground uppercase tracking-wider">Language</span>
                        <span className="font-bold uppercase text-emerald-500">{actualPlan.language || 'EN'}</span>
                    </GlassCard>
                    <GlassCard className="p-3 flex flex-col items-center justify-center bg-purple-500/5 border-purple-500/20">
                        <span className="text-xs text-muted-foreground uppercase tracking-wider">Topics</span>
                        <span className="font-bold text-purple-500">{actualPlan.subtopics?.length || 0}</span>
                    </GlassCard>
                </div>
            )}

            {/* Planner Notes */}
            {actualPlan.planner_notes && (
                <div className="bg-muted/50 border-l-4 border-yellow-500 p-4 rounded-r-lg">
                    <h4 className="flex items-center gap-2 font-semibold text-yellow-500 mb-1">
                        <Lightbulb className="h-4 w-4" />
                        Planner Notes
                    </h4>
                    <p className="text-sm text-muted-foreground italic">
                        "{actualPlan.planner_notes}"
                    </p>
                </div>
            )}

            {/* Overall Objectives */}
            {objectives && objectives.length > 0 && (
                <div className="space-y-3">
                    <h3 className="text-lg font-semibold flex items-center gap-2">
                        <Target className="h-5 w-5 text-primary" />
                        Key Objectives
                    </h3>
                    <ul className="list-disc list-inside space-y-1 bg-white/5 p-4 rounded-lg border border-white/10">
                        {renderList(objectives)}
                    </ul>
                </div>
            )}

            {/* Subtopics Accordion */}
            {actualPlan.subtopics && actualPlan.subtopics.length > 0 && (
                <div className="space-y-3">
                    <h3 className="text-lg font-semibold flex items-center gap-2">
                        <List className="h-5 w-5 text-primary" />
                        Curriculum Breakdown
                    </h3>
                    <Accordion type="single" collapsible className="w-full space-y-2">
                        {actualPlan.subtopics.map((topic: any, idx: number) => (
                            <AccordionItem
                                key={idx}
                                value={`item-${idx}`}
                                className="border border-white/10 bg-white/5 rounded-lg px-2"
                            >
                                <AccordionTrigger className="hover:no-underline py-3">
                                    <div className="flex flex-1 items-center justify-between mr-4 text-left">
                                        <span className="font-medium flex gap-2 items-center">
                                            <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold">
                                                {idx + 1}
                                            </span>
                                            {topic.title}
                                        </span>
                                        {/* Only show metadata if available and valid */}
                                        {(topic.estimated_time_minutes || topic.weight) && (
                                            <div className="flex gap-2 text-xs">
                                                {topic.estimated_time_minutes && (
                                                    <Badge variant="secondary" className="gap-1">
                                                        <Clock className="h-3 w-3" />
                                                        {topic.estimated_time_minutes}m
                                                    </Badge>
                                                )}
                                                {topic.weight && (
                                                    <Badge variant="outline" className="gap-1">
                                                        Weight: {topic.weight}%
                                                    </Badge>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                </AccordionTrigger>
                                <AccordionContent className="pb-4 pt-1 px-2 space-y-4">
                                    {/* Learning Outcomes */}
                                    {topic.learning_outcomes && (
                                        <div>
                                            <h5 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                                                <GraduationCap className="h-3 w-3" /> Learning Outcomes
                                            </h5>
                                            <ul className="list-disc list-inside text-sm space-y-1 pl-1">
                                                {renderList(topic.learning_outcomes)}
                                            </ul>
                                        </div>
                                    )}

                                    {/* Dynamic Grid: If key_terms exists, 2 cols, else 1 col */}
                                    <div className={`grid gap-4 ${topic.key_terms ? 'md:grid-cols-2' : 'grid-cols-1'}`}>
                                        {/* Key Terms */}
                                        {topic.key_terms && topic.key_terms.length > 0 && (
                                            <div className="bg-black/20 p-3 rounded-md">
                                                <h5 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                                                    <BookOpen className="h-3 w-3" /> Key Terms
                                                </h5>
                                                <div className="flex flex-wrap gap-1">
                                                    {topic.key_terms.map((term: string, i: number) => (
                                                        <Badge key={i} variant="secondary" className="text-xs font-normal">
                                                            {term}
                                                        </Badge>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {/* Suggested Examples */}
                                        {topic.suggested_examples && topic.suggested_examples.length > 0 && (
                                            <div className="bg-black/20 p-3 rounded-md">
                                                <h5 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                                                    <Brain className="h-3 w-3" /> Examples
                                                </h5>
                                                <ul className="list-disc list-inside text-sm space-y-1">
                                                    {renderList(topic.suggested_examples)}
                                                </ul>
                                            </div>
                                        )}
                                    </div>

                                    {/* Questions */}
                                    <div className="flex items-center gap-2 text-xs text-muted-foreground bg-primary/5 p-2 rounded">
                                        <HelpCircle className="h-3 w-3" />
                                        <span>Suggested Questions: <strong>{topic.suggested_questions}</strong></span>
                                    </div>
                                </AccordionContent>
                            </AccordionItem>
                        ))}
                    </Accordion>
                </div>
            )}

            {/* Assessment Strategy */}
            {actualPlan.assessment_strategy && (
                <div className="space-y-3">
                    <h3 className="text-lg font-semibold flex items-center gap-2">
                        <CheckCircle2 className="h-5 w-5 text-primary" />
                        Assessment Strategy
                    </h3>
                    <GlassCard className="p-4 bg-muted/30">
                        <div className="grid md:grid-cols-2 gap-4">
                            <div>
                                <span className="text-xs font-semibold uppercase text-muted-foreground">Format</span>
                                <div className="flex flex-wrap gap-2 mt-2">
                                    {actualPlan.assessment_strategy.format?.map((fmt: string, i: number) => (
                                        <Badge key={i} variant="outline" className="capitalize">{fmt.replace('-', ' ')}</Badge>
                                    ))}
                                </div>
                            </div>
                            <div>
                                <span className="text-xs font-semibold uppercase text-muted-foreground">Notes</span>
                                <p className="text-sm mt-1 text-muted-foreground">
                                    {actualPlan.assessment_strategy.notes}
                                </p>
                            </div>
                        </div>
                    </GlassCard>
                </div>
            )}
        </div>
    );
};
