/** @type {import('next').NextConfig} */
const nextConfig = {
  // En desarrollo local, proxiar /api/* al backend Python en :8000
  // En producción (Vercel), el vercel.json maneja el routing
  ...(process.env.NODE_ENV === 'development' && {
    async rewrites() {
      return [
        {
          source: '/api/:path*',
          destination: 'http://localhost:8000/api/:path*',
        },
      ]
    },
  }),
}

export default nextConfig
