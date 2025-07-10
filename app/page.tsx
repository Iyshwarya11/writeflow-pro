"use client";

export const dynamic = 'force-dynamic';

import { useState, useEffect, useRef } from 'react';
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
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
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
  LogIn,
  UserPlus
} from 'lucide-react';
import { getApiClientInstance } from '@/lib/api';

interface Document {
  id: string;
  title: string;
  content: string;
  last_modified: string;
  word_count: number;
  shared: boolean;
  starred: boolean;
  tags: string[];
  language: string;
  reading_time: number;
  collaborators: string[];
  version: number;
  is_public: boolean;
}

interface Suggestion {
  id: string;
  type: 'grammar' | 'style' | 'clarity' | 'tone' | 'plagiarism' | 'vocabulary';
  text: string;
  suggestion: string;
  explanation: string;
  position: { start: number; end: number };
  severity: 'error' | 'warning' | 'info';
  confidence: number;
}

interface Comment {
  id: string;
  text: string;
  author: string;
  timestamp: string;
  position: { start: number; end: number };
  resolved: boolean;
}

interface WritingGoal {
  type: 'word_count' | 'time' | 'pages';
  target: number;
  current: number;
  deadline?: Date;
}

interface User {
  id: string;
  email: string;
  full_name: string;
}

export default function DocumentEditor() {
  // Authentication state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [showAuthDialog, setShowAuthDialog] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [authForm, setAuthForm] = useState({
    email: '',
    password: '',
    full_name: ''
  });

  // Document state
  const [documents, setDocuments] = useState<Document[]>([]);
  const [activeDocument, setActiveDocument] = useState<Document | null>(null);
  const [content, setContent] = useState('');

  // UI state
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
      try {
        const apiClient = getApiClientInstance();
        if (apiClient.isAuthenticated()) {
          const userData = await apiClient.getCurrentUser();
          setUser(userData);
          setIsAuthenticated(true);
          await loadDocuments();
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        getApiClientInstance().clearToken();
      }
    };

    checkAuth();
  }, []);

  // Load documents
  const loadDocuments = async () => {
    try {
      const docs = await getApiClientInstance().getDocuments();
      setDocuments(docs);
      if (docs.length > 0 && !activeDocument) {
        setActiveDocument(docs[0]);
        setContent(docs[0].content);
      }
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  // Authentication handlers
  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const apiClient = getApiClientInstance();
      if (authMode === 'login') {
        await apiClient.login({
          username: authForm.email,
          password: authForm.password
        });
      } else {
        await apiClient.register({
          email: authForm.email,
          password: authForm.password,
          full_name: authForm.full_name
        });
        await apiClient.login({
          username: authForm.email,
          password: authForm.password
        });
      }
      
      const userData = await apiClient.getCurrentUser();
      setUser(userData);
      setIsAuthenticated(true);
      setShowAuthDialog(false);
      await loadDocuments();
    } catch (error) {
      console.error('Authentication failed:', error);
      alert('Authentication failed. Please try again.');
    }
  };

  const handleLogout = async () => {
    try {
      await getApiClientInstance().logout();
      setIsAuthenticated(false);
      setUser(null);
      setDocuments([]);
      setActiveDocument(null);
      setContent('');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  // Generate suggestions with debouncing
  useEffect(() => {
    if (!isAuthenticated || !activeDocument) return;

    const generateSuggestions = async () => {
      try {
        if (content.trim().length > 10) {
          const newSuggestions = await getApiClientInstance().generateSuggestions({
            document_id: activeDocument.id,
            content,
            writing_goal: writingGoal,
            language: selectedLanguage,
          });
          setSuggestions(newSuggestions);
        }
      } catch (error) {
        console.error('Failed to generate suggestions:', error);
      }
    };

    const debounceTimer = setTimeout(generateSuggestions, 2000);
    return () => clearTimeout(debounceTimer);
  }, [content, writingGoal, selectedLanguage, activeDocument, isAuthenticated]);

  // Auto-save functionality
  useEffect(() => {
    if (!isAuthenticated || !activeDocument || content === activeDocument.content) return;

    const autoSave = setTimeout(async () => {
      setIsAutoSaving(true);
      try {
        const updatedDoc = await getApiClientInstance().updateDocument(activeDocument.id, {
          content,
          word_count: wordCount
        });
        setActiveDocument(updatedDoc);
        setDocuments(prev => prev.map(doc => 
          doc.id === activeDocument.id ? updatedDoc : doc
        ));
      } catch (error) {
        console.error('Auto-save failed:', error);
      } finally {
        setIsAutoSaving(false);
      }
    }, 3000);

    return () => clearTimeout(autoSave);
  }, [content, activeDocument, wordCount, isAuthenticated]);

  // Update analytics
  useEffect(() => {
    const words = content.trim().split(/\s+/).filter(word => word.length > 0);
    setWordCount(words.length);
    setReadingTime(Math.ceil(words.length / 200));
    
    const avgWordsPerSentence = words.length / (content.split(/[.!?]+/).length - 1 || 1);
    setGradeLevel(Math.min(Math.max(Math.floor(avgWordsPerSentence * 0.4 + 6), 6), 16));
    
    setWritingGoals(prev => prev.map(goal => 
      goal.type === 'word_count' ? { ...goal, current: words.length } : goal
    ));
  }, [content]);

  // Document handlers
  const createNewDocument = async () => {
    try {
      const newDoc = await getApiClientInstance().createDocument({
        title: 'Untitled Document',
        content: '',
        tags: [],
        language: selectedLanguage,
        writing_goal: writingGoal
      });
      setDocuments(prev => [newDoc, ...prev]);
      setActiveDocument(newDoc);
      setContent('');
    } catch (error) {
      console.error('Failed to create document:', error);
    }
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setContent(e.target.value);
  };

  const applySuggestion = async (suggestion: Suggestion) => {
    const newContent = content.slice(0, suggestion.position.start) + 
                      suggestion.suggestion + 
                      content.slice(suggestion.position.end);
    setContent(newContent);
    
    try {
      await getApiClientInstance().applySuggestion(suggestion.id);
      setSuggestions(prev => prev.filter(s => s.id !== suggestion.id));
    } catch (error) {
      console.error('Failed to apply suggestion:', error);
    }
  };

  const dismissSuggestion = async (suggestionId: string) => {
    try {
      await getApiClientInstance().dismissSuggestion(suggestionId);
      setSuggestions(prev => prev.filter(s => s.id !== suggestionId));
    } catch (error) {
      console.error('Failed to dismiss suggestion:', error);
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

  const filteredDocuments = documents.filter(doc => 
    doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    doc.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  // Show authentication dialog if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold">WriteFlow Pro</span>
            </div>
            <CardTitle>{authMode === 'login' ? 'Welcome Back' : 'Create Account'}</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleAuth} className="space-y-4">
              {authMode === 'register' && (
                <div>
                  <Label htmlFor="full_name">Full Name</Label>
                  <Input
                    id="full_name"
                    type="text"
                    value={authForm.full_name}
                    onChange={(e) => setAuthForm(prev => ({ ...prev, full_name: e.target.value }))}
                    required
                  />
                </div>
              )}
              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={authForm.email}
                  onChange={(e) => setAuthForm(prev => ({ ...prev, email: e.target.value }))}
                  required
                />
              </div>
              <div>
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={authForm.password}
                  onChange={(e) => setAuthForm(prev => ({ ...prev, password: e.target.value }))}
                  required
                />
              </div>
              <Button type="submit" className="w-full">
                {authMode === 'login' ? 'Sign In' : 'Create Account'}
              </Button>
            </form>
            <div className="mt-4 text-center">
              <Button
                variant="link"
                onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}
              >
                {authMode === 'login' 
                  ? "Don't have an account? Sign up" 
                  : "Already have an account? Sign in"
                }
              </Button>
            </div>
          </CardContent>
        </Card>
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
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <FileText className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold">WriteFlow Pro</span>
              </div>
              <Separator orientation="vertical" className="h-6" />
              <div className="flex items-center space-x-2">
                <span className="text-sm text-muted-foreground">
                  {activeDocument?.title || 'Untitled Document'}
                </span>
                <Badge variant="outline" className="text-xs">
                  v{activeDocument?.version || 1}
                </Badge>
                {isAutoSaving && (
                  <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                    <span>Saving...</span>
                  </div>
                )}
                <div className="flex items-center space-x-1">
                  {isOnline ? (
                    <Wifi className="w-4 h-4 text-green-500" />
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
              <span className="text-sm text-muted-foreground">
                Welcome, {user?.full_name}
              </span>
              <Button variant="ghost" size="sm" onClick={() => setFocusMode(!focusMode)}>
                <Focus className="w-4 h-4 mr-2" />
                Focus
              </Button>
              <Button variant="ghost" size="sm">
                <Share2 className="w-4 h-4 mr-2" />
                Share
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setDarkMode(!darkMode)}
              >
                {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
              </Button>
              <Button variant="ghost" size="sm" onClick={handleLogout}>
                Logout
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
                            className={`p-3 rounded-lg cursor-pointer transition-colors group ${
                              activeDocument?.id === doc.id
                                ? 'bg-primary/10 border border-primary/20'
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
                                  {new Date(doc.last_modified).toLocaleDateString()}
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
                                <Button variant="ghost" size="sm">
                                  <Star className={`w-3 h-3 ${doc.starred ? 'fill-yellow-400 text-yellow-400' : ''}`} />
                                </Button>
                                <Button variant="ghost" size="sm">
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
                              {doc.word_count} words • {new Date(doc.last_modified).toLocaleDateString()}
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
                </div>
                
                <div className="flex items-center space-x-2">
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
                <div className="bg-card rounded-lg shadow-lg border border-border/50 min-h-[600px] p-8">
                  <textarea
                    ref={editorRef}
                    value={content}
                    onChange={handleContentChange}
                    className="w-full h-full min-h-[500px] resize-none border-none outline-none bg-transparent text-base leading-relaxed font-medium"
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
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="suggestions">AI</TabsTrigger>
                    <TabsTrigger value="analytics">Analytics</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="suggestions" className="space-y-4 mt-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2 text-sm">
                        <Sparkles className="w-4 h-4 text-yellow-500" />
                        <span className="font-medium">AI Suggestions</span>
                      </div>
                      <Badge variant="secondary" className="text-xs">
                        {suggestions.length}
                      </Badge>
                    </div>
                    
                    <ScrollArea className="h-[calc(100vh-300px)]">
                      <div className="space-y-3">
                        {suggestions.map((suggestion) => (
                          <Card key={suggestion.id} className={`p-3 ${getSuggestionColor(suggestion.type)}`}>
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
                                <div className="text-sm font-medium text-green-600 mb-3">
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
                                </div>
                              </div>
                            </div>
                          </Card>
                        ))}
                        {suggestions.length === 0 && (
                          <div className="text-center text-muted-foreground py-8">
                            <Sparkles className="w-8 h-8 mx-auto mb-2 opacity-50" />
                            <p>Start writing to get AI suggestions</p>
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
                </Tabs>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}