/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: { unoptimized: true },
  async rewrites() {
    return [
      {
        source: '/api/ai/:path*',
        destination: 'http://localhost:8000/api/ai/:path*',
      },
      {
        source: '/api/ai/plagiarism/:path*',
        destination: 'http://localhost:8000/api/ai/plagiarism/:path*',
      },
      {
        source: '/api/plagiarism/:path*',
        destination: 'http://localhost:8000/api/ai/plagiarism/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
