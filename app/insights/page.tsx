'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  Target,
  BookOpen,
  Clock,
  Users,
  Award,
  BarChart3,
  PieChart,
  LineChart
} from 'lucide-react';
import { useSession } from "next-auth/react";

export default function Insights() {
  const { data: session } = useSession();
  const userEmail = session?.user?.email;
  const [timeRange, setTimeRange] = useState('week');
  const [insightsData, setInsightsData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showDocs, setShowDocs] = useState(false);
  const [userDocs, setUserDocs] = useState<any[]>([]);

  useEffect(() => {
    if (!userEmail) return;
    const fetchInsights = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch('http://localhost:8000/api/ai/insights', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: userEmail, time_range: timeRange }),
        });
        if (!response.ok) {
          console.error('Insights API Error:', response.status, response.statusText);
          setError(`API Error: ${response.status}`);
          setInsightsData(null);
          return;
        }
        const data = await response.json();
        setInsightsData(data);
      } catch (err: any) {
        setError(err.message || 'Unknown error');
        setInsightsData(null);
      } finally {
        setLoading(false);
      }
    };
    fetchInsights();
  }, [timeRange, userEmail]);

  // Fetch user documents when showDocs is toggled on
  useEffect(() => {
    if (showDocs && userEmail) {
      fetch(`/api/documents?user_id=${encodeURIComponent(userEmail)}&limit=100`)
        .then(res => res.json())
        .then(docs => {
          console.log('Fetched user documents for insights:', docs);
          setUserDocs(docs);
        });
    }
  }, [showDocs, userEmail]);

  const achievements = [
    { id: 1, title: 'Writing Streak', description: '7 days in a row', icon: '🔥', unlocked: true },
    { id: 2, title: 'Word Master', description: '10,000 words written', icon: '📝', unlocked: true },
    { id: 3, title: 'Grammar Guru', description: '95% accuracy rate', icon: '✅', unlocked: false },
    { id: 4, title: 'Clarity Champion', description: 'Consistently clear writing', icon: '💡', unlocked: true }
  ];

  return (
    <div className="min-h-screen bg-gray-50 w-full">
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
                <h1 className="text-lg font-semibold text-gray-900">Writing Insights</h1>
                <p className="text-sm text-gray-500">Track your progress and improve your writing</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Button
                variant={timeRange === 'week' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setTimeRange('week')}
              >
                Week
              </Button>
              <Button
                variant={timeRange === 'month' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setTimeRange('month')}
              >
                Month
              </Button>
              <Button
                variant={timeRange === 'year' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setTimeRange('year')}
              >
                Year
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="w-full px-4 py-6">
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Total Words</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-gray-900">{Number(insightsData?.performance_metrics?.total_words) || 0}</div>
                  <div className="flex items-center text-sm text-green-600 mt-1">
                    <TrendingUp className="w-4 h-4 mr-1" />
                    <span>+{Number(insightsData?.performance_metrics?.improvement_rate) || 0}% from last week</span>
                  </div>
                </CardContent>
              </Card>

              <Card className="cursor-pointer" onClick={() => setShowDocs(v => !v)}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Documents</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-gray-900">{Number(insightsData?.performance_metrics?.total_documents) || 0}</div>
                  <div className="flex items-center text-sm text-blue-600 mt-1">
                    <BookOpen className="w-4 h-4 mr-1" />
                    <span>Created this week</span>
                  </div>
                  {/* Expandable document list */}
                  {showDocs && (
                    <div className="mt-4 border-t pt-2">
                      <div className="font-semibold mb-2">Your Documents</div>
                      {userDocs.length === 0 ? (
                        <div className="text-sm text-gray-500">No documents found.</div>
                      ) : (
                        <ul className="space-y-2">
                          {userDocs.map((doc) => (
                            <li key={doc.id} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                              <Link href={`/editor?doc=${encodeURIComponent(doc.id)}`} className="font-medium text-blue-700 hover:underline">
                                {doc.title}
                              </Link>
                              <span className="text-xs text-gray-500">{doc.last_modified ? new Date(doc.last_modified).toLocaleDateString() : ''}</span>
                              <span className="text-xs text-gray-700">Score: {doc.score ?? 'N/A'}</span>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Average Score</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-gray-900">{Number(insightsData?.performance_metrics?.average_score) || 0}%</div>
                  <div className="flex items-center text-sm text-green-600 mt-1">
                    <Target className="w-4 h-4 mr-1" />
                    <span>Above baseline</span>
                  </div>
                </CardContent>
              </Card>

              {/* Remove the Time Spent card from the overview grid */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Time Spent Per Day</CardTitle>
                </CardHeader>
                <CardContent>
                  {(() => {
                    const mins = Number(insightsData?.performance_metrics?.time_spent_per_day) || 0;
                    const h = Math.floor(mins / 60);
                    const m = mins % 60;
                    return <div className="text-2xl font-bold text-gray-900">{h}:{m.toString().padStart(2, '0')}</div>;
                  })()}
                </CardContent>
              </Card>
            </div>

            {/* Remove Daily Writing Activity and Words written and quality scores over time */}
            {/* Remove Common Issues section */}
          </TabsContent>

          <TabsContent value="performance" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Average Score</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-gray-900">{Number(insightsData?.performance_metrics?.average_score) || 0}%</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Words Written</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-gray-900">{Number(insightsData?.performance_metrics?.total_words) || 0}</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Documents Created</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-gray-900">{Number(insightsData?.performance_metrics?.total_documents) || 0}</div>
                </CardContent>
              </Card>
            <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Writing Streak</CardTitle>
              </CardHeader>
              <CardContent>
                  <div className="text-2xl font-bold text-gray-900">{Number(insightsData?.performance_metrics?.writing_streak) || 0} days</div>
                </CardContent>
              </Card>
                      </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Vocabulary Diversity</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-lg text-gray-900">Unique Words: {Number(insightsData?.performance_metrics?.unique_words) || 0}</div>
                  <div className="text-sm text-gray-600">Diversity: {Number(insightsData?.performance_metrics?.vocabulary_diversity) || 0}%</div>
              </CardContent>
            </Card>
            <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Readability</CardTitle>
              </CardHeader>
              <CardContent>
                  <div className="text-lg text-gray-900">Score: {Number(insightsData?.performance_metrics?.readability_score) || 0}</div>
                  <div className="text-sm text-gray-600">Avg. Sentence Length: {Number(insightsData?.performance_metrics?.avg_sentence_length) || 0}</div>
              </CardContent>
            </Card>
            <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Tone & Clarity</CardTitle>
              </CardHeader>
              <CardContent>
                  <div className="text-lg text-gray-900">Tone: {insightsData?.performance_metrics?.tone || 'N/A'}</div>
                  <div className="text-sm text-gray-600">Clarity: {Number(insightsData?.performance_metrics?.clarity_score) || 0}%</div>
              </CardContent>
            </Card>
            <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Best Document</CardTitle>
              </CardHeader>
              <CardContent>
                  <div className="text-lg text-gray-900">{insightsData?.performance_metrics?.best_document?.title || 'N/A'}</div>
                  <div className="text-sm text-gray-600">Score: {Number(insightsData?.performance_metrics?.best_document?.score) || 0}</div>
                  <div className="text-xs text-gray-500">{insightsData?.performance_metrics?.best_document?.date ? new Date(insightsData.performance_metrics.best_document.date).toLocaleDateString() : ''}</div>
              </CardContent>
            </Card>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Top Improvement Areas</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="list-disc pl-5">
                    {(insightsData?.improvement_areas || []).slice(0, 3).map((area: string, idx: number) => (
                      <li key={idx} className="text-sm text-gray-700">{area}</li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Writing Frequency</CardTitle>
                  </CardHeader>
                  <CardContent>
                  <div className="text-lg text-gray-900">Days Active This Week: {Number(insightsData?.performance_metrics?.days_active_this_week) || 0}</div>
                  <div className="text-sm text-gray-600">Days Active This Month: {Number(insightsData?.performance_metrics?.days_active_this_month) || 0}</div>
                  </CardContent>
                </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}