FROM node:22-slim AS builder

LABEL org.opencontainers.image.source=https://github.com/ssciwr/mondey
LABEL org.opencontainers.image.description="MONDEY frontend production image"

ARG MONDEY_API_URL

WORKDIR /app

COPY package.json ./

COPY pnpm-lock.yaml ./

RUN npm install -g pnpm && pnpm install

COPY . .

RUN echo "VITE_MONDEY_API_URL=${MONDEY_API_URL}" > .env && pnpm run build

FROM nginx:1.27.1

COPY --from=builder /app/build /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf
