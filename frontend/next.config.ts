import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  agentRules: false,
  allowedDevOrigins: ["127.0.0.1"],
};

export default nextConfig;
