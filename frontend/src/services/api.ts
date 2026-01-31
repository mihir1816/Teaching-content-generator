const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export interface PlanRequest {
  level: string;
  style: string;
  topics: string;
  description: string;
  language?: string;
}

export interface YTRequest {
  video: string;
  plan_text: string;
  level: string;
  style: string;
  topics: string[];
}

export interface ArticleRequest {
  url: string;
  plan_text: string;
  topics: string[];
  level: string;
  style: string;
}

export interface TopicRequest {
  plan_text: string;
  level: string;
  style: string;
}

export interface FileUploadRequest {
  file: File;
  plan_text: string;
  topics: string[];
  level: string;
  style: string;
  language?: string;
}

export interface CombinedRequest {
  videos?: string[];
  articles?: string[];
  files?: File[];
  plan_text: string;
  topics: string[];
  level: string;
  style: string;
}

// Helper function to handle PPT downloads for all routes
const downloadPPTHelper = async (filename: string, prefix: string) => {
  const response = await fetch(`${API_BASE_URL}/api/${prefix}/download_ppt/${filename}`);
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    if (errorData?.error) {
      throw new Error(errorData.error);
    }
    throw new Error("Failed to download PPT");
  }
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
};

export const apiService = {
  // Download functions for each pipeline
  downloadPPT: async (filename: string) => {
    return downloadPPTHelper(filename, "topic_pipeline");
  },

  downloadYoutubePPT: async (filename: string) => {
    return downloadPPTHelper(filename, "yt_pipeline");
  },

  downloadArticlePPT: async (filename: string) => {
    return downloadPPTHelper(filename, "article_pipeline");
  },

  downloadFileUploadPPT: async (filename: string) => {
    return downloadPPTHelper(filename, "file_upload");
  },

  downloadCombinedPPT: async (filename: string) => {
    return downloadPPTHelper(filename, "combined_pipeline");
  },

  generatePlan: async (data: PlanRequest) => {
    const response = await fetch(`${API_BASE_URL}/api/plan/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to generate plan');
    return response.json();
  },

  editPlan: async (data: PlanRequest & { user_edits: string }) => {
    // Since backend has no dedicated edit endpoint, we regenerate with feedback in description
    const refinementPrompt = `\n\n[USER FEEDBACK FOR REFINEMENT]: ${data.user_edits}\n Please update the plan based on this feedback.`;

    const payload = {
      ...data,
      description: (data.description || "") + refinementPrompt
    };

    const response = await fetch(`${API_BASE_URL}/api/plan/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error('Failed to edit plan');
    return response.json();
  },

  generateYTContent: async (data: YTRequest) => {
    const response = await fetch(`${API_BASE_URL}/api/yt_pipeline/run_yt_pipeline`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to generate content');
    return response.json();
  },

  generateArticleContent: async (data: ArticleRequest) => {
    const response = await fetch(`${API_BASE_URL}/api/article_pipeline/run_article_pipeline`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to generate content');
    return response.json();
  },

  generateTopicContent: async (data: TopicRequest) => {
    const response = await fetch(`${API_BASE_URL}/api/topic_pipeline/run_topic_name_pipeline`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to generate content');
    return response.json();
  },

  generateFileContent: async (data: FileUploadRequest) => {
    const formData = new FormData();
    formData.append('file', data.file);
    formData.append('plan_text', data.plan_text);
    formData.append('topics', JSON.stringify(data.topics));
    formData.append('level', data.level);
    formData.append('style', data.style);

    const response = await fetch(`${API_BASE_URL}/api/file_upload/run_file_upload_pipeline`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) throw new Error('Failed to generate content');
    return response.json();
  },

  generateCombinedContent: async (data: CombinedRequest) => {
    const formData = new FormData();

    if (data.videos && data.videos.length > 0) {
      formData.append('videos', JSON.stringify(data.videos));
    }
    if (data.articles && data.articles.length > 0) {
      formData.append('articles', JSON.stringify(data.articles));
    }
    if (data.files) {
      data.files.forEach(file => {
        formData.append('files', file);
      });
    }

    formData.append('plan_text', data.plan_text);
    formData.append('topics', JSON.stringify(data.topics));
    formData.append('level', data.level);
    formData.append('style', data.style);

    const response = await fetch(`${API_BASE_URL}/api/combined_pipeline/run_combined_pipeline`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) throw new Error('Failed to generate content');
    return response.json();
  },
};
