FROM node:22-alpine

# Enable corepack for pnpm support
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

# Copy dependency files first for better layer caching
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

RUN pnpm install --frozen-lockfile

COPY . .

CMD ["pnpm", "run", "dev"]
