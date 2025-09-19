/** @type {import('next').NextConfig} */
const nextConfig = {
  // PWA Configuration
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ]
  },
  // Image optimization
  images: {
    domains: ['localhost', '68.183.59.147'],
    formats: ['image/webp', 'image/avif'],
  },
  // Compression and optimization
  compress: true,
  poweredByHeader: false,
  // Service worker for PWA
  async rewrites() {
    return [
      {
        source: '/sw.js',
        destination: '/_next/static/sw.js',
      },
      // Proxy API requests to backend
      {
        source: '/api/backend/:path*',
        destination: 'http://68.183.59.147:8000/:path*',
      },
    ]
  },
}

module.exports = nextConfig 