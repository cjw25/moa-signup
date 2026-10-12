/** @type {import('next').NextConfig} */
const nextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${process.env.MONITOR_API_URL || "http://127.0.0.1:5200"}/api/:path*` }];
  },
};

export default nextConfig;
