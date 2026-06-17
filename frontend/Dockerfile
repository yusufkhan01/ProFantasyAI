# ---- Build stage ----
FROM node:22-alpine AS build

WORKDIR /app

COPY package*.json .npmrc ./
RUN npm ci

COPY . .

# The API base URL must be baked in at build time for a static SPA.
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# ---- Runtime stage ----
FROM nginx:alpine AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
