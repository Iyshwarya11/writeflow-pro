'use client';

import { useSession, signIn, signOut } from "next-auth/react";
import { useState, useEffect } from "react";
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  FileText, 
  TrendingUp, 
  Target, 
  BookOpen, 
  PlusCircle,
  Search,
  Settings,
  Bell,
  User,
  CheckCircle,
  Clock,
  BarChart3
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Bar, BarChart, Legend } from 'recharts';

export default function Dashboard() {
  const { data: session, status } = useSession();
  const [showUser, setShowUser] = useState(false);
  const [recentDocuments, setRecentDocuments] = useState([]);
  const [userStats, setUserStats] = useState<any>(null);
  const [insights, setInsights] = useState<any>(null);
  const [activityChart, setActivityChart] = useState<any[]>([]);
  const [improvementAreas, setImprovementAreas] = useState<string[]>([]);
  const [achievements, setAchievements] = useState<any[]>([]);

  useEffect(() => {
    if (session?.user?.email) {
      fetch(`/api/users/${encodeURIComponent(session.user.email)}/statistics`)
        .then(res => res.json())
        .then(data => setUserStats(data));
      fetch('/api/ai/insights', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: session.user.email, time_range: 'week' })
      })
        .then(res => res.json())
        .then(data => {
          setInsights(data);
          setActivityChart(data.activity_chart || []);
          setImprovementAreas(data.improvement_areas || []);
          setAchievements(data.achievements || []);
        });
      fetch(`/api/documents?user_id=${encodeURIComponent(session.user.email)}&limit=5`)
        .then(res => res.json())
        .then(data => setRecentDocuments(data));
    }
  }, [session?.user?.email]);

  if (status === "loading") return <div>Loading...</div>;
  if (!session) {
    signIn();
    return null;
  }
  // Only define user after session is confirmed
  const user = session.user;

  return (
    <div className="min-h-screen w-full bg-gray-50">
      {/* Header */}
      <header className="flex justify-between items-center p-4 bg-white shadow">
        <div className="text-2xl font-bold tracking-tight text-blue-700">BonMot</div>
        <div className="relative flex items-center gap-2">
          {user && (
            <button
              className="flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-100"
              onClick={() => setShowUser((v) => !v)}
              onBlur={() => setTimeout(() => setShowUser(false), 200)}
            >
              <User className="w-5 h-5" />
              <span className="font-medium">{user.name || user.email}</span>
            </button>
          )}
          <button
            className="ml-2 px-3 py-2 rounded bg-red-50 text-red-600 hover:bg-red-100 border border-red-200 transition"
            onClick={() => signOut({ callbackUrl: '/login' })}
          >
            Logout
          </button>
          {showUser && user && (
            <div className="absolute right-0 mt-2 w-64 bg-white border rounded shadow p-4 z-10">
              <div className="mb-2 font-bold text-lg">User Details</div>
              <div><b>Email:</b> {user.email}</div>
              {user.name && <div><b>Name:</b> {user.name}</div>}
              {user.image && <div className="mt-2"><img src={user.image} alt="avatar" className="w-12 h-12 rounded-full" /></div>}
              {/* Add more fields if available */}
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="w-full px-4 py-6">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome back!</h1>
          <p className="text-gray-600">Let's continue improving your writing.</p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Link href="/editor">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer border-2 border-transparent hover:border-green-500">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center space-x-2">
                  <PlusCircle className="w-5 h-5 text-green-600" />
                  <span>New Document</span>
                </CardTitle>
                <CardDescription>Start writing with AI-powered assistance</CardDescription>
              </CardHeader>
            </Card>
          </Link>

          <Link href="/insights">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer border-2 border-transparent hover:border-blue-500">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="w-5 h-5 text-blue-600" />
                  <span>View Insights</span>
                </CardTitle>
                <CardDescription>Analyze your writing patterns</CardDescription>
              </CardHeader>
            </Card>
          </Link>

          <Link href="/plagiarism">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer border-2 border-transparent hover:border-purple-500">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center space-x-2">
                  <Search className="w-5 h-5 text-purple-600" />
                  <span>Check Plagiarism</span>
                </CardTitle>
                <CardDescription>Verify content originality</CardDescription>
              </CardHeader>
            </Card>
          </Link>
        </div>

        {/* Advanced Analytics Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          {/* Writing Activity Chart */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Writing Activity (Last 7 Days)</CardTitle>
            </CardHeader>
            <CardContent style={{ height: 250 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={activityChart} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" fontSize={12} />
                  <YAxis fontSize={12} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="words" fill="#3b82f6" name="Words" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
          {/* Score Trend Chart */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Score Trend (Last 7 Days)</CardTitle>
            </CardHeader>
            <CardContent style={{ height: 250 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={activityChart} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" fontSize={12} />
                  <YAxis fontSize={12} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="score" stroke="#10b981" name="Score" strokeWidth={2} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
        {/* Achievements */}
        <div className="mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Achievements</CardTitle>
            </CardHeader>
            <CardContent>
              {achievements.length === 0 ? (
                <div className="text-gray-500">No achievements yet.</div>
              ) : (
                <div className="flex flex-wrap gap-4">
                  {achievements.map((ach, idx) => (
                    <div key={idx} className={`flex items-center gap-2 px-3 py-2 rounded border ${ach.unlocked ? 'border-green-500 bg-green-50' : 'border-gray-300 bg-gray-100 opacity-60'}`}>
                      <span className="text-2xl">{ach.icon}</span>
                      <div>
                        <div className="font-semibold">{ach.title}</div>
                        <div className="text-xs text-gray-500">{ach.description}</div>
                      </div>
                      {ach.unlocked && <CheckCircle className="w-4 h-4 text-green-500 ml-2" />}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
        {/* Inspiration Card Placeholder */}
        <Card className="bg-gradient-to-r from-green-100 to-blue-100 border-0 shadow-none mb-8">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="w-6 h-6 text-green-600" />
              <span>Inspiration for Today</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <blockquote className="italic text-lg text-gray-700 text-center py-6">
              "The art of writing is the art of discovering what you believe."<br />
              <span className="block mt-2 text-sm text-gray-500">— Gustave Flaubert</span>
            </blockquote>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}