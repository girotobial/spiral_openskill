FROM node:20-alpine as build
WORKDIR /app

COPY dashboard/package*.json ./
RUN npm ci

COPY dashboard/ ./
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build


FROM nginx:stable-alpine3.21
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80