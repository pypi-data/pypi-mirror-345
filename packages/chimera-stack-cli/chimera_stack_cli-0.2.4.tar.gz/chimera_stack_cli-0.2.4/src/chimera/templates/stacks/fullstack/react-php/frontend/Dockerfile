FROM node:20-alpine

WORKDIR /app

# Install create-react-app globally
RUN npm install -g create-react-app

# Copy existing project files (if any)
COPY . .

# Bootstrap React app if package.json is missing:
# 1. Generate CRA in temporary directory to avoid conflict.
# 2. Move generated files into /app (overwriting none / merging).
# 3. Remove temporary directory.
RUN if [ ! -f "package.json" ]; then \
    echo "Bootstrapping new React (TypeScript) app..." && \
    npx create-react-app temp --template typescript --use-npm && \
    cp -R temp/. ./ && \
    rm -rf temp; \
    fi

# Always install dependencies afterwards (package.json now guaranteed)
RUN npm install

# Ensure axios and cors-anywhere are installed (idempotent)
RUN npm list axios >/dev/null 2>&1 || npm install axios && \
    npm list cors-anywhere >/dev/null 2>&1 || npm install cors-anywhere

# Expose the port for development server
EXPOSE 3000

# Start development server
CMD ["npm", "start"]
