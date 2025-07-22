'use client';
import { signIn } from "next-auth/react";
import { useState } from "react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="flex flex-col md:flex-row w-full max-w-3xl bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Logo & Feature Section */}
        <div className="hidden md:flex flex-col items-center justify-center bg-gradient-to-br from-blue-100 to-green-100 p-8 w-1/2">
          <div className="flex flex-col items-center">
            {/* Logo/Icon */}
            <div className="bg-blue-600 rounded-full p-4 mb-4 shadow-lg">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="48" height="48" rx="24" fill="#2563eb"/>
                <text x="50%" y="56%" textAnchor="middle" fill="white" fontSize="28" fontWeight="bold" fontFamily="sans-serif" dy=".3em">B</text>
              </svg>
            </div>
            <h2 className="text-3xl font-bold text-blue-700 mb-2">BonMot</h2>
            <p className="text-lg text-gray-700 text-center max-w-xs mb-4">AI-powered writing assistant for flawless, impactful communication.</p>
            <ul className="text-gray-600 text-sm space-y-2 mt-4">
              <li>✓ Real-time grammar & style suggestions</li>
              <li>✓ Personalized writing insights</li>
              <li>✓ Secure, user-based document history</li>
            </ul>
          </div>
        </div>
        {/* Login Form Section */}
        <div className="flex-1 flex items-center justify-center p-8">
          <form
            className="w-full max-w-sm"
            onSubmit={async (e) => {
              e.preventDefault();
              setError("");
              const res = await signIn("credentials", {
                email,
                password,
                redirect: false,
              });
              if (res?.error) setError("Invalid email or password");
              else window.location.href = "/";
            }}
          >
            <div className="md:hidden flex flex-col items-center mb-8">
              <div className="bg-blue-600 rounded-full p-3 mb-2 shadow-lg">
                <svg width="36" height="36" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect width="48" height="48" rx="24" fill="#2563eb"/>
                  <text x="50%" y="56%" textAnchor="middle" fill="white" fontSize="22" fontWeight="bold" fontFamily="sans-serif" dy=".3em">B</text>
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-blue-700">BonMot</h2>
            </div>
            <h1 className="text-2xl font-bold mb-6 text-center">Login</h1>
            <input
              className="w-full mb-4 p-2 border rounded"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="Email"
              type="email"
              required
            />
            <input
              className="w-full mb-4 p-2 border rounded"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="Password"
              required
            />
            {error && <div className="text-red-500 mb-2 text-center">{error}</div>}
            <button
              className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
              type="submit"
            >
              Login
            </button>
          </form>
        </div>
      </div>
    </div>
  );
} 