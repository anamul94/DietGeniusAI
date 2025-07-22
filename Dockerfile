# Multi-stage build for optimized Next.js production image
FROM node:20-alpine AS deps

# Install dependencies only when needed
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./
RUN npm ci --only=production && npm cache clean --force

# Rebuild the source code only when needed
FROM node:20-alpine AS builder

WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Accept build arguments
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_TRANSCRIPTION_API_URL

# Set environment variables for build
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_TRANSCRIPTION_API_URL=$NEXT_PUBLIC_TRANSCRIPTION_API_URL
ENV NODE_ENV=production

# Build the application
RUN npm run build

# Production image, copy all the files and run next
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/api/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })"

# Start the application
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]