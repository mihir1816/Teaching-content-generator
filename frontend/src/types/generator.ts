export type Level = "beginner" | "intermediate" | "advanced";
export type Style = "concise" | "detailed" | "exam-prep";

export interface GeneratorFormData {
  topic: string;
  description?: string;
  youtubeLink?: string;
  documents?: File[];
  level: Level;
  style: Style;
}

export interface PlanItem {
  id: string;
  title: string;
  content: string;
  order: number;
}

export interface GeneratedPlan {
  items: PlanItem[];
  metadata: {
    topic: string;
    level: Level;
    style: Style;
  };
}
