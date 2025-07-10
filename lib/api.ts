const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Types
export interface LoginRequest {
  username: string; // FastAPI OAuth2 uses 'username' field for email
  password: string;
}

export interface RegisterRequest {
  email: string;
  full_name: string;
  password: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  subscription_tier: string;
  preferences: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  title: string;
  content: string;
  user_id: string;
  word_count: number;
  reading_time: number;
  version: number;
  collaborators: string[];
  created_at: string;
  updated_at: string;
  last_modified: string;
  shared: boolean;
  starred: boolean;
  tags: string[];
  language: string;
  writing_goal: string;
  is_public: boolean;
}

export interface Suggestion {
  id: string;
  document_id: string;
  user_id: string;
  type: 'grammar' | 'style' | 'clarity' | 'tone' | 'plagiarism' | 'vocabulary';
  text: string;
  suggestion: string;
  explanation: string;
  position: { start: number; end: number };
  severity: 'error' | 'warning' | 'info';
  confidence: number;
  is_applied: boolean;
  is_dismissed: boolean;
  created_at: string;
}

export interface Comment {
  id: string;
  document_id: string;
  user_id: string;
  author: string;
  text: string;
  position: { start: number; end: number };
  resolved: boolean;
  created_at: string;
  updated_at: string;
  timestamp: string;
}

// API Client Class
class APIClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    // Load token from localStorage if available
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('access_token');
    }
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const config: RequestInit = {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch {
          errorData = { detail: `HTTP ${response.status}: ${response.statusText}` };
        }
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Auth methods
  async login(credentials: LoginRequest): Promise<{ access_token: string; token_type: string }> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Login failed');
    }

    const data = await response.json();
    this.token = data.access_token;
    
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', data.access_token);
    }

    return data;
  }

  async register(userData: RegisterRequest): Promise<User> {
    return this.request<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  async logout(): Promise<void> {
    await this.request('/auth/logout', { method: 'POST' });
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
    }
  }

  // Document methods
  async getDocuments(): Promise<Document[]> {
    return this.request<Document[]>('/documents/');
  }

  async getDocument(id: string): Promise<Document> {
    return this.request<Document>(`/documents/${id}`);
  }

  async createDocument(document: Partial<Document>): Promise<Document> {
    return this.request<Document>('/documents/', {
      method: 'POST',
      body: JSON.stringify(document),
    });
  }

  async updateDocument(id: string, updates: Partial<Document>): Promise<Document> {
    return this.request<Document>(`/documents/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async deleteDocument(id: string): Promise<void> {
    await this.request(`/documents/${id}`, { method: 'DELETE' });
  }

  async duplicateDocument(id: string): Promise<Document> {
    return this.request<Document>(`/documents/${id}/duplicate`, {
      method: 'POST',
    });
  }

  async searchDocuments(query: string): Promise<Document[]> {
    return this.request<Document[]>(`/documents/search?q=${encodeURIComponent(query)}`);
  }

  // AI Suggestions methods
  async generateSuggestions(data: {
    document_id: string;
    content: string;
    writing_goal?: string;
    language?: string;
  }): Promise<Suggestion[]> {
    return this.request<Suggestion[]>('/ai/suggestions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getDocumentSuggestions(documentId: string): Promise<Suggestion[]> {
    return this.request<Suggestion[]>(`/ai/suggestions/${documentId}`);
  }

  async applySuggestion(suggestionId: string): Promise<void> {
    await this.request(`/ai/suggestions/${suggestionId}/apply`, {
      method: 'PUT',
    });
  }

  async dismissSuggestion(suggestionId: string): Promise<void> {
    await this.request(`/ai/suggestions/${suggestionId}/dismiss`, {
      method: 'PUT',
    });
  }

  async analyzeTone(content: string): Promise<any> {
    return this.request('/ai/tone-analysis', {
      method: 'POST',
      body: JSON.stringify({ content }),
    });
  }

  async checkPlagiarism(content: string): Promise<any> {
    return this.request('/ai/plagiarism-check', {
      method: 'POST',
      body: JSON.stringify({ content }),
    });
  }

  // Analytics methods
  async getDocumentAnalytics(documentId: string): Promise<any> {
    return this.request(`/analytics/document/${documentId}`);
  }

  async getReadabilityAnalysis(documentId: string): Promise<any> {
    return this.request(`/analytics/document/${documentId}/readability`);
  }

  async extractKeywords(documentId: string): Promise<any> {
    return this.request(`/analytics/document/${documentId}/keywords`);
  }

  async getUserStats(): Promise<any> {
    return this.request('/analytics/user/stats');
  }

  // Comments methods
  async createComment(comment: {
    document_id: string;
    text: string;
    position: { start: number; end: number };
  }): Promise<Comment> {
    return this.request<Comment>('/comments/', {
      method: 'POST',
      body: JSON.stringify(comment),
    });
  }

  async getDocumentComments(documentId: string): Promise<Comment[]> {
    return this.request<Comment[]>(`/comments/document/${documentId}`);
  }

  async updateComment(commentId: string, updates: { text?: string; resolved?: boolean }): Promise<Comment> {
    return this.request<Comment>(`/comments/${commentId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async deleteComment(commentId: string): Promise<void> {
    await this.request(`/comments/${commentId}`, { method: 'DELETE' });
  }

  async resolveComment(commentId: string): Promise<void> {
    await this.request(`/comments/${commentId}/resolve`, {
      method: 'PUT',
    });
  }

  // Utility methods
  isAuthenticated(): boolean {
    return !!this.token;
  }

  setToken(token: string): void {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  clearToken(): void {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
    }
  }
}

// Singleton instance
let apiClientInstance: APIClient | null = null;

// Export function to get singleton instance
export function getApiClientInstance(): APIClient {
  if (!apiClientInstance && typeof window !== 'undefined') {
    apiClientInstance = new APIClient(API_BASE_URL);
  }
  
  if (!apiClientInstance) {
    throw new Error('API client can only be used in browser environment');
  }
  
  return apiClientInstance;
}