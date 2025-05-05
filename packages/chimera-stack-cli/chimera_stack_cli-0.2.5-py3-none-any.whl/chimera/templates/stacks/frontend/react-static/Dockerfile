# templates/stacks/frontend/react-static/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package.json and potentially package-lock.json
COPY package*.json ./

# Install dependencies with legacy peer deps to avoid strict dependency requirements
RUN npm install --legacy-peer-deps

# Copy the rest of the application code
COPY . .

# production build
RUN npm run build

# ---------- development ----------
ARG FRONTEND_PORT=3000
ENV FRONTEND_PORT=${FRONTEND_PORT}

# Expose the port the app runs on
EXPOSE ${FRONTEND_PORT}

# Command to run the app
CMD ["sh","-c","npm run dev -- --host 0.0.0.0 --port ${FRONTEND_PORT}"]
