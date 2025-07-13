/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/auth/google/callback',
        destination: '/auth/callback',
      },
    ];
  },
};

module.exports = nextConfig;