FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build        # prod
ENV FRONTEND_PORT=${FRONTEND_PORT}
EXPOSE ${FRONTEND_PORT}
CMD ["sh","-c","npm run dev -- --host 0.0.0.0 --port ${FRONTEND_PORT}"]
