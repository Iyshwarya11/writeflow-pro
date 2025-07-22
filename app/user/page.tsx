'use client';
import { useSession, signIn } from "next-auth/react";
import { useEffect, useState } from "react";

export default function UserProfile() {
  const { data: session, status } = useSession();
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    if (session?.user?.email) {
      setError(null);
      fetch(`/api/users/${encodeURIComponent(session.user.email)}`)
        .then(async res => {
          if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `API Error: ${res.status}`);
          }
          return res.json();
        })
        .then(data => {
          setProfile(data);
          setLoading(false);
        })
        .catch(err => {
          setError(err.message || 'Unknown error');
          setLoading(false);
        });
    }
  }, [session?.user?.email]);
  if (status === "loading" || loading) return <div className="p-8">Loading...</div>;
  if (!session) {
    signIn();
    return null;
  }
  if (error) return <div className="p-8 text-red-600">Error: {error}</div>;
  if (!profile) return <div className="p-8">No profile found.</div>;
  return (
    <div className="w-full p-8 px-4">
      <h1 className="text-2xl font-bold mb-4">User Profile</h1>
      <div className="mb-4">
        <div><b>Email:</b> {profile.email}</div>
        {profile.full_name && <div><b>Full Name:</b> {profile.full_name}</div>}
        {profile.subscription_tier && <div><b>Subscription:</b> {profile.subscription_tier}</div>}
        {profile.is_active !== undefined && <div><b>Active:</b> {profile.is_active ? 'Yes' : 'No'}</div>}
        {profile.preferences && <div><b>Preferences:</b> <pre>{JSON.stringify(profile.preferences, null, 2)}</pre></div>}
        <div><b>Joined:</b> {profile.created_at ? new Date(profile.created_at).toLocaleString() : 'N/A'}</div>
        <div><b>Last Login:</b> {profile.last_login ? new Date(profile.last_login).toLocaleString() : 'N/A'}</div>
      </div>
      <h2 className="text-xl font-semibold mb-2">Statistics</h2>
      <div className="mb-2">Total Documents: {profile.stats?.total_documents ?? 0}</div>
      <div className="mb-2">Total Words: {profile.stats?.total_words ?? 0}</div>
      <div className="mb-2">Average Score: {profile.stats?.average_score ?? 0}</div>
      <div className="mb-2">Writing Frequency: {profile.stats?.writing_frequency ?? 0}</div>
      <div className="mb-2">Best Score: {profile.stats?.best_score ?? 0}</div>
      <div className="mb-2">Average Words per Document: {profile.stats?.average_words_per_document ?? 0}</div>
    </div>
  );
} 