# the official pnpm image, the Node.js version is installed by pnpm from the devEngines pin in pnpm-lock.yaml
FROM ghcr.io/pnpm/pnpm:12.14.0 AS builder

LABEL org.opencontainers.image.source=https://github.com/ssciwr/mondey
LABEL org.opencontainers.image.description="MONDEY frontend production image"

ARG MONDEY_API_URL

WORKDIR /app

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

RUN pnpm install --frozen-lockfile

COPY . .

RUN echo "VITE_MONDEY_API_URL=${MONDEY_API_URL}" > .env && pnpm run build

FROM nginx:1.30.4-alpine-slim

COPY --from=builder /app/build /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf
