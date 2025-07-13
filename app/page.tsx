"use client";
import { useState, useEffect, useRef } from 'react';
import { apiClient, type Document as APIDocument, type Suggestion as APISuggestion, type Comment as APIComment } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { 
  FileText, 
  Save, 
  Download, 
  Share2, 
  Eye, 
  BarChart3, 
  Lightbulb, 
  CheckCircle, 
  AlertCircle,
  BookOpen,
  Moon,
  Sun,
  Plus,
  Folder,
  Search,
  Settings,
  Palette,
  Bold,
  Italic,
  Underline,
  AlignLeft,
  AlignCenter,
  AlignRight,
  List,
  Quote,
  Link,
  Zap,
  TrendingUp,
  Clock,
  Users,
  Copy,
  Trash2,
  Star,
  Filter,
  Calendar,
  Target,
  Award,
  Globe,
  Lock,
  Unlock,
  MessageSquare,
  History,
  RefreshCw,
  Type,
  Mic,
  MicOff,
  Play,
  Pause,
  Volume2,
  Languages,
  Bookmark,
  Tag,
  Archive,
  Upload,
  FileDown,
  Printer,
  Mail,
  Scissors,
  Clipboard,
  RotateCcw,
  RotateCw,
  ZoomIn,
  ZoomOut,
  Maximize,
  Minimize,
  PanelLeftClose,
  PanelRightClose,
  Focus,
  Brain,
  Sparkles,
  Shield,
  Database,
  Cloud,
  Wifi,
  WifiOff,
  Menu,
  X,
  Home,
  User,
  CreditCard,
  HelpCircle,
  LogOut
} from 'lucide-react';

interface Document extends Omit<APIDocument, 'last_modified'> {
  lastModified: Date;
}

interface OriginalDocument {
  id: string;
  title: string;
  content: string;
  lastModified: Date;
  wordCount: number;
  shared: boolean;
  starred: boolean;
  tags: string[];
  language: string;
  readingTime: number;
  collaborators: string[];
  version: number;
  isPublic: boolean;
}

interface Suggestion extends APISuggestion {
}

interface OriginalSuggestion {
  id: string;
  type: 'grammar' | 'style' | 'clarity' | 'tone' | 'plagiarism' | 'vocabulary';
  text: string;
  suggestion: string;
  explanation: string;
  position: { start: number; end: number };
  severity: 'error' | 'warning' | 'info';
  confidence: number;
}

interface Comment extends Omit<APIComment, 'timestamp'> {
  timestamp: Date;
}

interface OriginalComment {
  id: string;
  text: string;
  author: string;
  timestamp: Date;
  position: { start: number; end: number };
  resolved: boolean;
}

interface WritingGoal {
  type: 'word_count' | 'time' | 'pages';
  target: number;
  current: number;
  deadline?: Date;
}

export default function GrammarlyClone() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [user, setUser] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [registerForm, setRegisterForm] = useState({ email: '', full_name: '', password: '' });
  const [showRegister, setShowRegister] = useState(false);
  
  const [activeDocument, setActiveDocument] = useState<Document | null>(null);
  const [content, setContent] = useState('');
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [comments, setComments] = useState<Comment[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [showComments, setShowComments] = useState(true);
  const [writingGoal, setWritingGoal] = useState('professional');
  const [wordCount, setWordCount] = useState(0);
  const [readingTime, setReadingTime] = useState(0);
  const [gradeLevel, setGradeLevel] = useState(8);
  const [isAutoSaving, setIsAutoSaving] = useState(false);
  const [isOnline, setIsOnline] = useState(true);
  const [voiceRecording, setVoiceRecording] = useState(false);
  const [speechSynthesis, setSpeechSynthesis] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState('en-US');
  const [zoomLevel, setZoomLevel] = useState(100);
  const [darkMode, setDarkMode] = useState(false);
  const [focusMode, setFocusMode] = useState(false);
  const [clientDates, setClientDates] = useState<Record<string, string>>({});
  const [mounted, setMounted] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showLeftPanel, setShowLeftPanel] = useState(true);
  const [showRightPanel, setShowRightPanel] = useState(true);
  const [writingGoals, setWritingGoals] = useState<WritingGoal[]>([
    { type: 'word_count', target: 1000, current: 350 },
    { type: 'time', target: 60, current: 25 }
  ]);
  const [plagiarismScore, setPlagiarismScore] = useState(2);
  const [vocabularyScore, setVocabularyScore] = useState(85);
  const [toneAnalysis, setToneAnalysis] = useState({
    formal: 75,
    confident: 80,
    optimistic: 65,
    analytical: 90
  });
  
  const editorRef = useRef<HTMLTextAreaElement>(null);

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      if (apiClient.isAuthenticated()) {
        try {
          const userData = await apiClient.getCurrentUser();
          setUser(userData);
          setIsAuthenticated(true);
          await loadDocuments();
        } catch (error) {
          console.error('Auth check failed:', error);
          apiClient.clearToken();
          setIsAuthenticated(false);
        }
      }
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  // Load documents
  const loadDocuments = async () => {
    try {
      const docs = await apiClient.getDocuments();
      const formattedDocs = docs.map(doc => ({
        ...doc,
        lastModified: new Date(doc.last_modified)
      }));
      setDocuments(formattedDocs);
      
      if (formattedDocs.length > 0 && !activeDocument) {
        setActiveDocument(formattedDocs[0]);
        setContent(formattedDocs[0].content);
      }
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  // Load comments for active document
  useEffect(() => {
    const loadComments = async () => {
      if (activeDocument) {
        try {
          const apiComments = await apiClient.getDocumentComments(activeDocument.id);
          const formattedComments = apiComments.map(comment => ({
            ...comment,
            timestamp: new Date(comment.timestamp)
          }));
          setComments(formattedComments);
        } catch (error) {
          console.error('Failed to load comments:', error);
        }
      }
    };

    if (activeDocument && isAuthenticated) {
      loadComments();
    }
  }, [activeDocument, isAuthenticated]);

  // Generate suggestions when content changes
  useEffect(() => {
    const generateSuggestions = async () => {
      if (activeDocument && content.trim().length > 0 && isAuthenticated) {
        try {
          const apiSuggestions = await apiClient.generateSuggestions({
            document_id: activeDocument.id,
            content,
            writing_goal: writingGoal,
            language: selectedLanguage
          });
          setSuggestions(apiSuggestions);
        } catch (error) {
          console.error('Failed to generate suggestions:', error);
        }
      } else {
        setSuggestions([]);
      }
    };

    const timer = setTimeout(generateSuggestions, 1000);
    return () => clearTimeout(timer);
  }, [content, writingGoal, selectedLanguage, activeDocument, isAuthenticated]);

  useEffect(() => {
    if (activeDocument) {
      setContent(activeDocument.content);
    }
  }, [activeDocument]);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    const map: Record<string, string> = {};
    documents.forEach((doc) => {
      map[doc.id] = new Date(doc.lastModified).toLocaleDateString();
    });
    setClientDates(map);
  }, [documents]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const theme = localStorage.getItem('theme');
      if (theme === 'dark') {
        setDarkMode(true);
      }
    }
  }, []);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const focus = localStorage.getItem('focusMode');
      if (focus === 'true') {
        setFocusMode(true);
      }
    }
  }, []);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('theme', darkMode ? 'dark' : 'light');
    }
  }, [darkMode]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('focusMode', focusMode.toString());
    }
  }, [focusMode]);

  // Handle login
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.login({ username: loginForm.email, password: loginForm.password });
      const userData = await apiClient.getCurrentUser();
      setUser(userData);
      setIsAuthenticated(true);
      await loadDocuments();
      setLoginForm({ email: '', password: '' });
    } catch (error) {
      console.error('Login failed:', error);
      alert('Login failed. Please check your credentials.');
    }
  };

  // Handle register
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.register(registerForm);
      await apiClient.login({ username: registerForm.email, password: registerForm.password });
      const userData = await apiClient.getCurrentUser();
      setUser(userData);
      setIsAuthenticated(true);
      await loadDocuments();
      setRegisterForm({ email: '', full_name: '', password: '' });
      setShowRegister(false);
    } catch (error) {
      console.error('Registration failed:', error);
      alert('Registration failed. Please try again.');
    }
  };

  // Handle logout
  const handleLogout = async () => {
    try {
      await apiClient.logout();
      setUser(null);
      setIsAuthenticated(false);
      setDocuments([]);
      setActiveDocument(null);
      setContent('');
      setSuggestions([]);
      setComments([]);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  // Update analytics
  useEffect(() => {
    const words = content.trim().split(/\s+/).filter(word => word.length > 0);
    setWordCount(words.length);
    setReadingTime(Math.ceil(words.length / 200));
    
    const avgWordsPerSentence = words.length / (content.split(/[.!?]+/).length - 1 || 1);
    setGradeLevel(Math.min(Math.max(Math.floor(avgWordsPerSentence * 0.4 + 6), 6), 16));
    
    // Update writing goals
    setWritingGoals(prev => prev.map(goal => 
      goal.type === 'word_count' ? { ...goal, current: words.length } : goal
    ));
  }, [content]);

  // Auto-save simulation
  useEffect(() => {
    const autoSave = setTimeout(async () => {
      if (activeDocument && content !== activeDocument.content && isAuthenticated) {
        setIsAutoSaving(true);
        try {
          const updatedDoc = await apiClient.updateDocument(activeDocument.id, { content });
          const formattedDoc = {
            ...updatedDoc,
            lastModified: new Date(updatedDoc.last_modified)
          };
          
          setDocuments(prev => prev.map(doc => 
            doc.id === activeDocument.id ? formattedDoc : doc
          ));
          setActiveDocument(formattedDoc);
        } catch (error) {
          console.error('Auto-save failed:', error);
        } finally {
          setIsAutoSaving(false);
        }
      }
    }, 2000);

    return () => clearTimeout(autoSave);
  }, [content, activeDocument, wordCount, isAuthenticated]);

  // Online status detection
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    if (typeof window !== 'undefined') {
      window.addEventListener('online', handleOnline);
      window.addEventListener('offline', handleOffline);
      
      return () => {
        window.removeEventListener('online', handleOnline);
        window.removeEventListener('offline', handleOffline);
      };
    }
  }, []);

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setContent(e.target.value);
  };

  const applySuggestion = async (suggestion: Suggestion) => {
    try {
      await apiClient.applySuggestion(suggestion.id);
      const newContent = content.slice(0, suggestion.position.start) + 
                        suggestion.suggestion + 
                        content.slice(suggestion.position.end);
      setContent(newContent);
      setSuggestions(prev => prev.filter(s => s.id !== suggestion.id));
    } catch (error) {
      console.error('Failed to apply suggestion:', error);
    }
  };

  const dismissSuggestion = async (suggestionId: string) => {
    try {
      await apiClient.dismissSuggestion(suggestionId);
      setSuggestions(prev => prev.filter(s => s.id !== suggestionId));
    } catch (error) {
      console.error('Failed to dismiss suggestion:', error);
    }
  };

  const addComment = async (text: string, position: { start: number; end: number }) => {
    if (!activeDocument) return;
    
    try {
      const apiComment = await apiClient.createComment({
        document_id: activeDocument.id,
        text,
        position
      });
      const formattedComment = {
        ...apiComment,
        timestamp: new Date(apiComment.timestamp)
      };
      setComments(prev => [...prev, formattedComment]);
    } catch (error) {
      console.error('Failed to add comment:', error);
    }
  };

  const resolveComment = async (commentId: string) => {
    try {
      await apiClient.resolveComment(commentId);
      setComments(prev => prev.map(comment => 
        comment.id === commentId ? { ...comment, resolved: true } : comment
      ));
    } catch (error) {
      console.error('Failed to resolve comment:', error);
    }
  };

  const toggleStar = async (docId: string) => {
    const doc = documents.find(d => d.id === docId);
    if (!doc) return;
    
    try {
      const updatedDoc = await apiClient.updateDocument(docId, { starred: !doc.starred });
      const formattedDoc = {
        ...updatedDoc,
        lastModified: new Date(updatedDoc.last_modified)
      };
      setDocuments(prev => prev.map(d => 
        d.id === docId ? formattedDoc : d
      ));
    } catch (error) {
      console.error('Failed to toggle star:', error);
    }
  };

  const duplicateDocument = async (doc: Document) => {
    try {
      const duplicatedDoc = await apiClient.duplicateDocument(doc.id);
      const formattedDoc = {
        ...duplicatedDoc,
        lastModified: new Date(duplicatedDoc.last_modified)
      };
      setDocuments(prev => [...prev, formattedDoc]);
    } catch (error) {
      console.error('Failed to duplicate document:', error);
    }
  };

  const createNewDocument = async () => {
    try {
      console.log('erkejnioerni')
      const newDoc = await apiClient.createDocument({
        title: 'Untitled Document',
        content: '',
        tags: [],
        language: 'en-US',
        writing_goal: 'professional',
        is_public: false,
        shared: false,
        starred: false
      });
      const formattedDoc = {
        ...newDoc,
        lastModified: new Date(newDoc.last_modified)
      };
      setDocuments(prev => [...prev, formattedDoc]);
      setActiveDocument(formattedDoc);
      setContent('');
    } catch (error) {
      console.error('Failed to create document:', error);
    }
  };

  const exportDocument = (format: 'pdf' | 'docx' | 'txt' | 'md') => {
    console.log(`Exporting document as ${format}`);
  };

  const startVoiceRecording = () => {
    setVoiceRecording(true);
    setTimeout(() => {
      setVoiceRecording(false);
      setContent(prev => prev + " This text was added via voice recording.");
    }, 3000);
  };

  const toggleSpeechSynthesis = () => {
    setSpeechSynthesis(!speechSynthesis);
    if (!speechSynthesis && typeof window !== 'undefined' && 'speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(content);
      window.speechSynthesis.speak(utterance);
    } else if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  };

  const getSuggestionIcon = (type: string) => {
    switch (type) {
      case 'grammar': return <AlertCircle className="w-4 h-4" />;
      case 'style': return <Palette className="w-4 h-4" />;
      case 'clarity': return <Lightbulb className="w-4 h-4" />;
      case 'tone': return <Users className="w-4 h-4" />;
      case 'vocabulary': return <Brain className="w-4 h-4" />;
      case 'plagiarism': return <Shield className="w-4 h-4" />;
      default: return <CheckCircle className="w-4 h-4" />;
    }
  };

  const getSuggestionColor = (type: string) => {
    switch (type) {
      case 'grammar': return 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950';
      case 'style': return 'border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950';
      case 'clarity': return 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950';
      case 'tone': return 'border-purple-200 bg-purple-50 dark:border-purple-800 dark:bg-purple-950';
      case 'vocabulary': return 'border-orange-200 bg-orange-50 dark:border-orange-800 dark:bg-orange-950';
      case 'plagiarism': return 'border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-950';
      default: return 'border-gray-200 bg-gray-50 dark:border-gray-800 dark:bg-gray-950';
    }
  };

  const filteredDocuments = Array.isArray(documents)
    ? documents.filter(doc => 
        doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
      )
    : [];

  if (!mounted) {
    return null;
  }

  // Show login/register form if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-blue-50 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="bg-white rounded-lg shadow-xl p-8">
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-gradient-to-br from-emerald-500 to-blue-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <FileText className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent">
                WriteFlow Pro
              </h1>
              <p className="text-gray-600 mt-2">AI-powered writing assistant</p>
            </div>

            {!showRegister ? (
              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={loginForm.email}
                    onChange={(e) => setLoginForm(prev => ({ ...prev, email: e.target.value }))}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    value={loginForm.password}
                    onChange={(e) => setLoginForm(prev => ({ ...prev, password: e.target.value }))}
                    required
                  />
                </div>
                <Button type="submit" className="w-full">
                  Sign In
                </Button>
                <div className="text-center">
                  <button
                    type="button"
                    onClick={() => setShowRegister(true)}
                    className="text-sm text-emerald-600 hover:text-emerald-700"
                  >
                    Don't have an account? Sign up
                  </button>
                </div>
              </form>
            ) : (
              <form onSubmit={handleRegister} className="space-y-4">
                <div>
                  <Label htmlFor="full_name">Full Name</Label>
                  <Input
                    id="full_name"
                    type="text"
                    value={registerForm.full_name}
                    onChange={(e) => setRegisterForm(prev => ({ ...prev, full_name: e.target.value }))}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="reg_email">Email</Label>
                  <Input
                    id="reg_email"
                    type="email"
                    value={registerForm.email}
                    onChange={(e) => setRegisterForm(prev => ({ ...prev, email: e.target.value }))}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="reg_password">Password</Label>
                  <Input
                    id="reg_password"
                    type="password"
                    value={registerForm.password}
                    onChange={(e) => setRegisterForm(prev => ({ ...prev, password: e.target.value }))}
                    required
                  />
                </div>
                <Button type="submit" className="w-full">
                  Sign Up
                </Button>
                <div className="text-center">
                  <button
                    type="button"
                    onClick={() => setShowRegister(false)}
                    className="text-sm text-emerald-600 hover:text-emerald-700"
                  >
                    Already have an account? Sign in
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-emerald-500 to-blue-600 rounded-lg flex items-center justify-center mx-auto mb-4 animate-pulse">
            <FileText className="w-8 h-8 text-white" />
          </div>
          <p className="text-muted-foreground">Loading WriteFlow Pro...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${darkMode ? 'dark' : ''}`}>
      <div className="bg-background text-foreground">
        {/* Header */}
        <header className="border-b border-border bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/50">
          <div className="flex items-center justify-between px-6 py-3">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-blue-600 rounded-lg flex items-center justify-center">
                  <FileText className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent">
                  AI-writing assistant
                </span>
              </div>
              <Separator orientation="vertical" className="h-6" />
              <div className="flex items-center space-x-2">
                <span className="text-sm text-muted-foreground">
                  {user?.full_name}
                </span>
                <Separator orientation="vertical" className="h-4" />
                <span className="text-sm text-muted-foreground">
                  {activeDocument?.title || 'No document selected'}
                </span>
                {activeDocument && (
                  <Badge variant="outline" className="text-xs">
                    v{activeDocument.version}
                  </Badge>
                )}
                {isAutoSaving && (
                  <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                    <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                    <span>Saving...</span>
                  </div>
                )}
                <div className="flex items-center space-x-1">
                  {isOnline ? (
                    <Wifi className="w-4 h-4 text-emerald-500" />
                  ) : (
                    <WifiOff className="w-4 h-4 text-red-500" />
                  )}
                  <span className="text-xs text-muted-foreground">
                    {isOnline ? 'Online' : 'Offline'}
                  </span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <Button variant="ghost" size="sm" onClick={() => setFocusMode(!focusMode)}>
                <Focus className="w-4 h-4 mr-2" />
                Focus
              </Button>
              <Button variant="ghost" size="sm">
                <Share2 className="w-4 h-4 mr-2" />
                Share
              </Button>
              <Button variant="ghost" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
              <Button variant="ghost" size="sm">
                <Eye className="w-4 h-4 mr-2" />
                Preview
              </Button>
              <Button variant="ghost" size="sm" onClick={handleLogout}>
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setDarkMode(!darkMode)}
              >
                {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
              </Button>
            </div>
          </div>
        </header>

        <div className="flex h-[calc(100vh-73px)]">
          {/* Left Sidebar */}
          {showLeftPanel && !focusMode && (
            <div className="w-80 border-r border-border bg-card/30 backdrop-blur supports-[backdrop-filter]:bg-card/30">
              <div className="p-4">
                <div className="flex items-center space-x-2 mb-4">
                  <Button className="flex-1" size="sm" onClick={createNewDocument}>
                    <Plus className="w-4 h-4 mr-2" />
                    New Document
                  </Button>
                  <Button variant="outline" size="sm">
                    <Upload className="w-4 h-4" />
                  </Button>
                </div>
                
                <div className="relative mb-4">
                  <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="Search documents..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>

                <Tabs defaultValue="recent" className="w-full">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="recent">Recent</TabsTrigger>
                    <TabsTrigger value="starred">Starred</TabsTrigger>
                    <TabsTrigger value="shared">Shared</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="recent" className="mt-4">
                    <ScrollArea className="h-60">
                      <div className="space-y-2">
                        {filteredDocuments.map((doc) => (
                          <div
                            key={doc.id}
                            className={`p-3 rounded-lg cursor-pointer transition-all duration-200 group hover:shadow-md ${
                              activeDocument?.id === doc.id
                                ? 'bg-emerald-50 border border-emerald-200 dark:bg-emerald-950 dark:border-emerald-800'
                                : 'hover:bg-muted/50'
                            }`}
                            onClick={() => {
                              setActiveDocument(doc);
                              setContent(doc.content);
                            }}
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1 min-w-0">
                                <div className="font-medium text-sm truncate">{doc.title}</div>
                                <div className="text-xs text-muted-foreground mt-1">
                                  {doc.word_count} words • {doc.reading_time} min read
                                </div>
                                <div className="text-xs text-muted-foreground">
                                  {doc.lastModified.toLocaleDateString()}
                                </div>
                                {doc.tags.length > 0 && (
                                  <div className="flex flex-wrap gap-1 mt-2">
                                    {doc.tags.map((tag) => (
                                      <Badge key={tag} variant="secondary" className="text-xs">
                                        {tag}
                                      </Badge>
                                    ))}
                                  </div>
                                )}
                              </div>
                              <div className="flex flex-col space-y-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    toggleStar(doc.id);
                                  }}
                                >
                                  <Star className={`w-3 h-3 ${doc.starred ? 'fill-yellow-400 text-yellow-400' : ''}`} />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    duplicateDocument(doc);
                                  }}
                                >
                                  <Copy className="w-3 h-3" />
                                </Button>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  </TabsContent>
                  
                  <TabsContent value="starred" className="mt-4">
                    <ScrollArea className="h-60">
                      <div className="space-y-2">
                        {filteredDocuments.filter(doc => doc.starred).map((doc) => (
                          <div key={doc.id} className="p-3 rounded-lg border border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-950">
                            <div className="font-medium text-sm">{doc.title}</div>
                            <div className="text-xs text-muted-foreground mt-1">
                              {doc.word_count} words • {doc.lastModified.toLocaleDateString()}
                            </div>
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  </TabsContent>
                  
                  <TabsContent value="shared" className="mt-4">
                    <ScrollArea className="h-60">
                      <div className="space-y-2">
                        {filteredDocuments.filter(doc => doc.shared).map((doc) => (
                          <div key={doc.id} className="p-3 rounded-lg border border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950">
                            <div className="font-medium text-sm">{doc.title}</div>
                            <div className="text-xs text-muted-foreground mt-1">
                              Shared with {doc.collaborators.length} people
                            </div>
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  </TabsContent>
                </Tabs>

                <Separator className="my-4" />
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between text-sm">
                    <span>AI Suggestions</span>
                    <Switch
                      checked={showSuggestions}
                      onCheckedChange={setShowSuggestions}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span>Comments</span>
                    <Switch
                      checked={showComments}
                      onCheckedChange={setShowComments}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <div className="text-sm text-muted-foreground">Writing Goal</div>
                    <select
                      className="w-full px-3 py-2 text-sm border border-border rounded-md bg-background"
                      value={writingGoal}
                      onChange={(e) => setWritingGoal(e.target.value)}
                    >
                      <option value="professional">Professional</option>
                      <option value="academic">Academic</option>
                      <option value="creative">Creative</option>
                      <option value="casual">Casual</option>
                      <option value="technical">Technical</option>
                      <option value="marketing">Marketing</option>
                    </select>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="text-sm text-muted-foreground">Language</div>
                    <select
                      className="w-full px-3 py-2 text-sm border border-border rounded-md bg-background"
                      value={selectedLanguage}
                      onChange={(e) => setSelectedLanguage(e.target.value)}
                    >
                      <option value="en-US">English (US)</option>
                      <option value="en-GB">English (UK)</option>
                      <option value="es-ES">Spanish</option>
                      <option value="fr-FR">French</option>
                      <option value="de-DE">German</option>
                      <option value="it-IT">Italian</option>
                    </select>
                  </div>

                  <div className="space-y-3">
                    <div className="text-sm text-muted-foreground">Writing Goals</div>
                    {writingGoals.map((goal, index) => (
                      <Card key={index} className="p-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium capitalize">
                            {goal.type.replace('_', ' ')}
                          </span>
                          <span className="text-sm text-muted-foreground">
                            {goal.current}/{goal.target}
                          </span>
                        </div>
                        <Progress value={(goal.current / goal.target) * 100} className="h-2" />
                      </Card>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Main Editor Area */}
          <div className="flex-1 flex flex-col">
            {/* Enhanced Toolbar */}
            <div className="border-b border-border bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/50 p-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-1">
                  <Button variant="ghost" size="sm">
                    <Bold className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="sm">
                    <Italic className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="sm">
                    <Underline className="w-4 h-4" />
                  </Button>
                  <Separator orientation="vertical" className="h-6 mx-2" />
                  <Button variant="ghost" size="sm">
                    <AlignLeft className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="sm">
                    <AlignCenter className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="sm">
                    <AlignRight className="w-4 h-4" />
                  </Button>
                  <Separator orientation="vertical" className="h-6 mx-2" />
                  <Button variant="ghost" size="sm">
                    <List className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="sm">
                    <Quote className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="sm">
                    <Link className="w-4 h-4" />
                  </Button>
                  <Separator orientation="vertical" className="h-6 mx-2" />
                  <Button variant="ghost" size="sm">
                    <RotateCcw className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="sm">
                    <RotateCw className="w-4 h-4" />
                  </Button>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={startVoiceRecording}
                    className={voiceRecording ? 'text-red-500' : ''}
                  >
                    {voiceRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={toggleSpeechSynthesis}
                    className={speechSynthesis ? 'text-blue-500' : ''}
                  >
                    {speechSynthesis ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                  </Button>
                  <Separator orientation="vertical" className="h-6" />
                  <div className="flex items-center space-x-1">
                    <Button variant="ghost" size="sm" onClick={() => setZoomLevel(Math.max(50, zoomLevel - 10))}>
                      <ZoomOut className="w-4 h-4" />
                    </Button>
                    <span className="text-sm text-muted-foreground min-w-[3rem] text-center">
                      {zoomLevel}%
                    </span>
                    <Button variant="ghost" size="sm" onClick={() => setZoomLevel(Math.min(200, zoomLevel + 10))}>
                      <ZoomIn className="w-4 h-4" />
                    </Button>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => setShowLeftPanel(!showLeftPanel)}>
                    <PanelLeftClose className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => setShowRightPanel(!showRightPanel)}>
                    <PanelRightClose className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>

            {/* Editor */}
            <div className="flex-1 p-8 bg-gradient-to-br from-background via-background to-muted/20">
              <div className="max-w-4xl mx-auto">
                <div className="bg-card rounded-lg shadow-lg border border-border/50 min-h-[600px] p-8 transition-all duration-200 hover:shadow-xl">
                  <textarea
                    ref={editorRef}
                    value={content}
                    onChange={handleContentChange}
                    className="w-full h-full min-h-[500px] resize-none border-none outline-none bg-transparent text-base leading-relaxed font-medium placeholder:text-muted-foreground/50"
                    placeholder="Start writing your document..."
                    style={{ fontSize: `${zoomLevel}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Enhanced Stats Bar */}
            <div className="border-t border-border bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/50 p-3">
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <div className="flex items-center space-x-6">
                  <div className="flex items-center space-x-1">
                    <BookOpen className="w-4 h-4" />
                    <span>{wordCount} words</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Clock className="w-4 h-4" />
                    <span>{readingTime} min read</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <BarChart3 className="w-4 h-4" />
                    <span>Grade {gradeLevel}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Shield className="w-4 h-4" />
                    <span>{plagiarismScore}% plagiarism</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Brain className="w-4 h-4" />
                    <span>{vocabularyScore}% vocabulary</span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="outline" className="text-xs">
                    {suggestions.length} suggestions
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {comments.filter(c => !c.resolved).length} comments
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {writingGoal}
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {selectedLanguage}
                  </Badge>
                </div>
              </div>
            </div>
          </div>

          {/* Enhanced Right Sidebar */}
          {showRightPanel && !focusMode && (
            <div className="w-96 border-l border-border bg-card/30 backdrop-blur supports-[backdrop-filter]:bg-card/30">
              <div className="p-4">
                <Tabs defaultValue="suggestions" className="w-full">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="suggestions">AI</TabsTrigger>
                    <TabsTrigger value="analytics">Analytics</TabsTrigger>
                    <TabsTrigger value="comments">Comments</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="suggestions" className="space-y-4 mt-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2 text-sm">
                        <Sparkles className="w-4 h-4 text-emerald-500" />
                        <span className="font-medium">AI Suggestions</span>
                      </div>
                      <Badge variant="secondary" className="text-xs">
                        {suggestions.length}
                      </Badge>
                    </div>
                    
                    <div className="flex items-center space-x-2 mb-4">
                      <Button variant="outline" size="sm" className="text-xs">
                        <Filter className="w-3 h-3 mr-1" />
                        All
                      </Button>
                      <Button variant="ghost" size="sm" className="text-xs">Grammar</Button>
                      <Button variant="ghost" size="sm" className="text-xs">Style</Button>
                      <Button variant="ghost" size="sm" className="text-xs">Clarity</Button>
                    </div>
                    
                    <ScrollArea className="h-[calc(100vh-300px)]">
                      <div className="space-y-3">
                        {suggestions.map((suggestion) => (
                          <Card key={suggestion.id} className={`p-3 transition-all duration-200 hover:shadow-md ${getSuggestionColor(suggestion.type)}`}>
                            <div className="flex items-start space-x-2">
                              <div className="flex-shrink-0 mt-1">
                                {getSuggestionIcon(suggestion.type)}
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center space-x-2 mb-2">
                                  <Badge variant="outline" className="text-xs capitalize">
                                    {suggestion.type}
                                  </Badge>
                                  <Badge 
                                    variant={suggestion.severity === 'error' ? 'destructive' : 'secondary'}
                                    className="text-xs"
                                  >
                                    {suggestion.severity}
                                  </Badge>
                                  <Badge variant="outline" className="text-xs">
                                    {suggestion.confidence}%
                                  </Badge>
                                </div>
                                <div className="text-sm font-medium mb-1">
                                  "{suggestion.text}"
                                </div>
                                <div className="text-sm text-muted-foreground mb-2">
                                  {suggestion.explanation}
                                </div>
                                <div className="text-sm font-medium text-emerald-600 mb-3">
                                  Suggestion: "{suggestion.suggestion}"
                                </div>
                                <div className="flex space-x-2">
                                  <Button
                                    size="sm"
                                    onClick={() => applySuggestion(suggestion)}
                                    className="text-xs"
                                  >
                                    Apply
                                  </Button>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => dismissSuggestion(suggestion.id)}
                                    className="text-xs"
                                  >
                                    Dismiss
                                  </Button>
                                  <Button variant="ghost" size="sm" className="text-xs">
                                    <Lightbulb className="w-3 h-3" />
                                  </Button>
                                </div>
                              </div>
                            </div>
                          </Card>
                        ))}
                        {suggestions.length === 0 && (
                          <div className="text-center py-8 text-muted-foreground">
                            <CheckCircle className="w-12 h-12 mx-auto mb-3 text-emerald-500" />
                            <p className="text-sm">No suggestions found!</p>
                            <p className="text-xs">Your writing looks great.</p>
                          </div>
                        )}
                      </div>
                    </ScrollArea>
                  </TabsContent>
                  
                  <TabsContent value="analytics" className="space-y-4 mt-4">
                    <div className="flex items-center space-x-2 text-sm">
                      <TrendingUp className="w-4 h-4 text-blue-500" />
                      <span className="font-medium">Writing Analytics</span>
                    </div>
                    
                    <div className="space-y-4">
                      <Card className="p-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium">Readability Score</span>
                          <span className="text-sm text-muted-foreground">85/100</span>
                        </div>
                        <Progress value={85} className="h-2" />
                      </Card>
                      
                      <Card className="p-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium">Clarity Score</span>
                          <span className="text-sm text-muted-foreground">78/100</span>
                        </div>
                        <Progress value={78} className="h-2" />
                      </Card>
                      
                      <Card className="p-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium">Engagement Score</span>
                          <span className="text-sm text-muted-foreground">92/100</span>
                        </div>
                        <Progress value={92} className="h-2" />
                      </Card>

                      <Card className="p-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium">Plagiarism Check</span>
                          <span className="text-sm text-muted-foreground">{plagiarismScore}%</span>
                        </div>
                        <Progress value={plagiarismScore} className="h-2" />
                        <div className="text-xs text-muted-foreground mt-1">
                          {plagiarismScore < 5 ? 'Original content' : 'Some similarities found'}
                        </div>
                      </Card>

                      <Card className="p-4">
                        <CardHeader className="p-0 mb-3">
                          <CardTitle className="text-sm">Tone Analysis</CardTitle>
                        </CardHeader>
                        <CardContent className="p-0 space-y-2">
                          {Object.entries(toneAnalysis).map(([tone, score]) => (
                            <div key={tone} className="flex justify-between items-center text-sm">
                              <span className="capitalize">{tone}</span>
                              <div className="flex items-center space-x-2">
                                <Progress value={score} className="h-1 w-16" />
                                <span className="font-medium w-8">{score}%</span>
                              </div>
                            </div>
                          ))}
                        </CardContent>
                      </Card>
                      
                      <Card className="p-4">
                        <CardHeader className="p-0 mb-3">
                          <CardTitle className="text-sm">Writing Stats</CardTitle>
                        </CardHeader>
                        <CardContent className="p-0 space-y-2">
                          <div className="flex justify-between text-sm">
                            <span>Average sentence length</span>
                            <span className="font-medium">18 words</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span>Passive voice</span>
                            <span className="font-medium">12%</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span>Adverb usage</span>
                            <span className="font-medium">3%</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span>Reading level</span>
                            <span className="font-medium">Grade {gradeLevel}</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span>Vocabulary diversity</span>
                            <span className="font-medium">{vocabularyScore}%</span>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  </TabsContent>

                  <TabsContent value="comments" className="space-y-4 mt-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2 text-sm">
                        <MessageSquare className="w-4 h-4 text-blue-500" />
                        <span className="font-medium">Comments</span>
                      </div>
                      <Badge variant="secondary" className="text-xs">
                        {comments.filter(c => !c.resolved).length} active
                      </Badge>
                    </div>
                    
                    <ScrollArea className="h-[calc(100vh-300px)]">
                      <div className="space-y-3">
                        {comments.map((comment) => (
                          <Card key={comment.id} className={`p-3 transition-all duration-200 hover:shadow-md ${comment.resolved ? 'opacity-50' : ''}`}>
                            <div className="flex items-start space-x-2">
                              <div className="flex-shrink-0 mt-1">
                                <MessageSquare className="w-4 h-4" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center space-x-2 mb-2">
                                  <span className="text-sm font-medium">{comment.author}</span>
                                  <span className="text-xs text-muted-foreground">
                                    {new Date(comment.timestamp).toLocaleTimeString()}
                                  </span>
                                  {comment.resolved && (
                                    <Badge variant="outline" className="text-xs">
                                      Resolved
                                    </Badge>
                                  )}
                                </div>
                                <div className="text-sm mb-3">
                                  {comment.text}
                                </div>
                                {!comment.resolved && (
                                  <div className="flex space-x-2">
                                    <Button
                                      size="sm"
                                      onClick={() => resolveComment(comment.id)}
                                      className="text-xs"
                                    >
                                      Resolve
                                    </Button>
                                    <Button variant="ghost" size="sm" className="text-xs">
                                      Reply
                                    </Button>
                                  </div>
                                )}
                              </div>
                            </div>
                          </Card>
                        ))}
                        
                        <Card className="p-3 border-dashed">
                          <div className="space-y-2">
                            <Textarea
                              placeholder="Add a comment..."
                              className="text-sm"
                              rows={2}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                  e.preventDefault();
                                  const text = e.currentTarget.value.trim();
                                  if (text) {
                                    addComment(text, { start: 0, end: 0 });
                                    e.currentTarget.value = '';
                                  }
                                }
                              }}
                            />
                            <Button 
                              size="sm" 
                              className="text-xs"
                              onClick={(e) => {
                                const textarea = e.currentTarget.parentElement?.querySelector('textarea');
                                const text = textarea?.value.trim();
                                if (text) {
                                  addComment(text, { start: 0, end: 0 });
                                  if (textarea) textarea.value = '';
                                }
                              }}
                            >
                              Add Comment
                            </Button>
                          </div>
                        </Card>
                      </div>
                    </ScrollArea>
                  </TabsContent>
                </Tabs>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}