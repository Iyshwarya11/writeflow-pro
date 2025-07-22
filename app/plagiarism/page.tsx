'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  ArrowLeft,
  Search,
  Upload,
  FileText,
  AlertTriangle,
  CheckCircle,
  ExternalLink,
  Eye,
  Download,
  Share
} from 'lucide-react';
import { useRef } from 'react';
import { Document, Packer, Paragraph, TextRun } from 'docx';

interface PlagiarismResult {
  id: string;
  source: string;
  similarity: number;
  matchedText: string;
  url: string;
  type: 'web' | 'academic' | 'publication';
}

export default function PlagiarismChecker() {
  const [content, setContent] = useState('');
  const [isChecking, setIsChecking] = useState(false);
  const [results, setResults] = useState<PlagiarismResult[]>([]);
  const [overallScore, setOverallScore] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [rawApiResponse, setRawApiResponse] = useState<any>(null);
  const [recentChecks, setRecentChecks] = useState<any[]>([]);

  // Load recent checks from localStorage on mount
  useEffect(() => {
    const checks = JSON.parse(localStorage.getItem('plagiarism_recent_checks') || '[]');
    setRecentChecks(checks);
  }, []);

  // Save a recent check to localStorage
  const saveRecentCheck = (content: string, score: number) => {
    const checks = JSON.parse(localStorage.getItem('plagiarism_recent_checks') || '[]');
    const newCheck = {
      content: content.slice(0, 60) + (content.length > 60 ? '...' : ''),
      score,
      date: new Date().toISOString(),
    };
    const updated = [newCheck, ...checks].slice(0, 5);
    localStorage.setItem('plagiarism_recent_checks', JSON.stringify(updated));
    setRecentChecks(updated);
  };

  const handleCheck = async () => {
    if (!content.trim()) return;
    setIsChecking(true);
    try {
      const response = await fetch('/api/ai/plagiarism/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content, check_web: true, check_academic: true }),
      });
      if (!response.ok) {
        console.error('Plagiarism API Error:', response.status, response.statusText);
        setResults([]);
        setOverallScore(0);
        return;
      }
      const data = await response.json();
      console.log('Plagiarism API Response:', data); // Debug log
      setRawApiResponse(data);
      setOverallScore(data.overall_score);
      setResults(
        (data.matches || data.results || []).map((match: any) => ({
          id: match.id,
          source: match.source,
          similarity: match.similarity,
          matchedText: match.matched_text || match.matchedText || '',
          url: match.url,
          type: match.type,
        }))
      );
      saveRecentCheck(content, data.overall_score);
    } catch (error) {
      console.error('Plagiarism Fetch Error:', error);
      setResults([]);
      setOverallScore(0);
    } finally {
      setIsChecking(false);
    }
  };

  // File reading helpers
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    setUploadError(null);
    const file = e.target.files?.[0];
    if (!file) return;
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext === 'txt') {
      const text = await file.text();
      setContent(text);
    } else if (ext === 'docx') {
      try {
        // @ts-ignore
        const docx = await import('docx');
        const reader = new FileReader();
        reader.onload = async (ev) => {
          const arrayBuffer = ev.target?.result;
          if (!arrayBuffer) return;
          // @ts-ignore
          const doc = await docx.Document.load(arrayBuffer);
          // @ts-ignore
          const text = doc.getBody().getText();
          setContent(text);
        };
        reader.readAsArrayBuffer(file);
      } catch {
        setUploadError('DOCX support not available in this environment.');
      }
    } else if (ext === 'pdf') {
      try {
        // @ts-ignore
        const pdfjsLib = await import('pdfjs-dist/build/pdf');
        const reader = new FileReader();
        reader.onload = async (ev) => {
          const typedarray = new Uint8Array(ev.target?.result as ArrayBuffer);
          // @ts-ignore
          const pdf = await pdfjsLib.getDocument({ data: typedarray }).promise;
          let text = '';
          for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i);
            const content = await page.getTextContent();
            text += content.items.map((item: any) => item.str).join(' ') + '\n';
          }
          setContent(text);
        };
        reader.readAsArrayBuffer(file);
      } catch {
        setUploadError('PDF support not available in this environment.');
      }
    } else {
      setUploadError('Unsupported file type. Only .txt, .docx, .pdf supported.');
    }
  };

  const triggerFileInput = () => fileInputRef.current?.click();

  // Export report as Word docx
  const handleExport = async () => {
    const doc = new Document({
      sections: [
        {
          properties: {},
          children: [
            new Paragraph({
              children: [
                new TextRun({ text: 'Plagiarism Report', bold: true, size: 32 }),
              ],
              spacing: { after: 300 },
            }),
            new Paragraph({ text: `Originality Score: ${overallScore}%`, spacing: { after: 200 } }),
            new Paragraph({ text: 'Checked Content:', bold: true }),
            new Paragraph({ text: content, spacing: { after: 300 } }),
            new Paragraph({ text: 'Results:', bold: true, spacing: { after: 200 } }),
            ...results.map((result, idx) =>
              new Paragraph({
                children: [
                  new TextRun({ text: `${idx + 1}. Source: ${result.source} (${result.type})`, bold: true }),
                  new TextRun({ text: `\nSimilarity: ${result.similarity}%` }),
                  new TextRun({ text: `\nMatched Text: "${result.matchedText}"` }),
                  new TextRun({ text: `\nURL: ${result.url}` }),
                ],
                spacing: { after: 200 },
              })
            ),
          ],
        },
      ],
    });
    const blob = await Packer.toBlob(doc);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'plagiarism_report.docx';
    a.click();
    URL.revokeObjectURL(url);
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreStatus = (score: number) => {
    if (score >= 90) return 'Excellent';
    if (score >= 70) return 'Good';
    return 'Needs Review';
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'web': return '🌐';
      case 'academic': return '🎓';
      case 'publication': return '📄';
      default: return '📝';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 w-full">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="w-full px-4 py-0">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Link href="/">
                <Button variant="ghost" size="icon">
                  <ArrowLeft className="w-5 h-5" />
                </Button>
              </Link>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">Plagiarism Checker</h1>
                <p className="text-sm text-gray-500">Verify the originality of your content</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm" onClick={triggerFileInput}>
                <Upload className="w-4 h-4 mr-2" />
                Upload File
              </Button>
              <Button variant="outline" size="sm" onClick={handleExport}>
                <Download className="w-4 h-4 mr-2" />
                Export Report
              </Button>
              <input
                ref={fileInputRef}
                type="file"
                accept=".txt,.docx,.pdf"
                className="hidden"
                onChange={handleFileChange}
              />
            </div>
          </div>
        </div>
      </header>

      <div className="w-full px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Input Section */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Search className="w-5 h-5" />
                  <span>Check for Plagiarism</span>
                </CardTitle>
                <CardDescription>
                  Paste your content below or upload a file to check for potential plagiarism
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <textarea
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="Paste your content here to check for plagiarism..."
                    className="w-full h-64 p-4 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  />
                  
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-600">
                      {content.length} characters • {content.split(' ').filter(word => word.length > 0).length} words
                    </div>
                    <Button 
                      onClick={handleCheck}
                      disabled={!content.trim() || isChecking}
                    >
                      {isChecking ? (
                        <div className="flex items-center space-x-2">
                          <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                          <span>Checking...</span>
                        </div>
                      ) : (
                        <div className="flex items-center space-x-2">
                          <Search className="w-4 h-4" />
                          <span>Check Plagiarism</span>
                        </div>
                      )}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Results */}
            {(results.length > 0 || isChecking) && (
              <Card className="mt-6">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <FileText className="w-5 h-5" />
                    <span>Plagiarism Results</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {isChecking ? (
                    <div className="flex items-center justify-center py-12">
                      <div className="text-center">
                        <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                        <p className="text-gray-600">Scanning content for plagiarism...</p>
                        <p className="text-sm text-gray-500 mt-2">This may take a few moments</p>
                      </div>
                    </div>
                  ) : (
                    <Tabs defaultValue="overview" className="w-full">
                      <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="overview">Overview</TabsTrigger>
                        <TabsTrigger value="details">Detailed Results</TabsTrigger>
                      </TabsList>
                      
                      <TabsContent value="overview" className="space-y-4">
                        <div className="text-center py-6">
                          <div className={`text-4xl font-bold mb-2 ${getScoreColor(overallScore)}`}>
                            {overallScore}%
                          </div>
                          <div className="text-lg text-gray-600 mb-4">Originality Score</div>
                          <Badge variant={overallScore >= 90 ? 'default' : overallScore >= 70 ? 'secondary' : 'destructive'}>
                            {getScoreStatus(overallScore)}
                          </Badge>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div className="text-center p-4 bg-blue-50 rounded-lg">
                            <div className="text-2xl font-bold text-blue-600">{results.length}</div>
                            <div className="text-sm text-gray-600">Sources Found</div>
                          </div>
                          <div className="text-center p-4 bg-yellow-50 rounded-lg">
                            <div className="text-2xl font-bold text-yellow-600">
                              {results.reduce((sum, r) => sum + r.similarity, 0)}%
                            </div>
                            <div className="text-sm text-gray-600">Total Similarity</div>
                          </div>
                          <div className="text-center p-4 bg-green-50 rounded-lg">
                            <div className="text-2xl font-bold text-green-600">{overallScore}%</div>
                            <div className="text-sm text-gray-600">Original Content</div>
                          </div>
                        </div>
                      </TabsContent>
                      
                      <TabsContent value="details" className="space-y-4">
                        {results.map((result) => (
                          <Card key={result.id} className="border-l-4 border-l-yellow-400">
                            <CardHeader className="pb-2">
                              <div className="flex items-center justify-between">
                                <CardTitle className="text-base flex items-center space-x-2">
                                  <span>{getTypeIcon(result.type)}</span>
                                  <span>{result.source}</span>
                                </CardTitle>
                                <Badge variant="outline">{result.similarity}% match</Badge>
                              </div>
                            </CardHeader>
                            <CardContent>
                              <div className="space-y-3">
                                <div className="p-3 bg-yellow-50 rounded-lg">
                                  <p className="text-sm text-gray-900">"{result.matchedText}"</p>
                                </div>
                                <div className="flex items-center justify-between">
                                  <a 
                                    href={result.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center space-x-1 text-blue-600 hover:text-blue-800 text-sm"
                                  >
                                    <span>View Source</span>
                                    <ExternalLink className="w-3 h-3" />
                                  </a>
                                  <div className="flex items-center space-x-2">
                                    <Button variant="outline" size="sm">
                                      <Eye className="w-4 h-4 mr-1" />
                                      Preview
                                    </Button>
                                  </div>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </TabsContent>
                    </Tabs>
                  )}
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="space-y-6">
              {/* Quick Tips */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Quick Tips</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 text-sm">
                    <div className="flex items-start space-x-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span>Always cite your sources properly</span>
                    </div>
                    <div className="flex items-start space-x-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span>Use quotation marks for direct quotes</span>
                    </div>
                    <div className="flex items-start space-x-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span>Paraphrase instead of copying</span>
                    </div>
                    <div className="flex items-start space-x-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span>Check before submitting</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* File Upload */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Upload Document</CardTitle>
                  <CardDescription>Support for .docx, .pdf, .txt files</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                    <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-600 mb-2">Drop files here or click to browse</p>
                    <Button variant="outline" size="sm" onClick={triggerFileInput}>
                      Select Files
                    </Button>
                    {uploadError && <div className="text-red-500 text-xs mt-2">{uploadError}</div>}
                  </div>
                </CardContent>
              </Card>

              {/* Recent Checks */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Recent Checks</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {recentChecks.length === 0 ? (
                      <div className="text-gray-500 text-sm">No recent checks yet.</div>
                    ) : (
                      recentChecks.map((item, index) => (
                        <div key={index} className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50">
                          <div>
                            <div className="font-medium text-sm">{item.content}</div>
                            <div className="text-xs text-gray-500">{new Date(item.date).toLocaleString()}</div>
                          </div>
                          <Badge variant="outline">{item.score}%</Badge>
                        </div>
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}