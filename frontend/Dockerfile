# Studio Grade Frontend (Optimized for Local Hive)
FROM nginx:stable-alpine
WORKDIR /usr/share/nginx/html

# Copy the pre-built distribution from the host
COPY dist/ .

# Inject Nginx configuration
COPY nginx.conf /etc/nginx/templates/default.conf.template
ENV BACKEND_URL=http://backend:8055
EXPOSE 80

CMD ["/bin/sh", "-c", "envsubst '${BACKEND_URL}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'"]
