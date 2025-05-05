# React Static Template

Welcome to your ChimeraStack-generated React application with Vite and Tailwind CSS!

## Features

- **React 18** with TypeScript support
- **Vite** for blazing-fast development and builds
- **Tailwind CSS** for utility-first styling
- **Docker** containerization
- **Nginx** proxy for production-ready deployment

## Getting Started

```bash
# Start the development environment
docker compose up -d

# View logs
docker compose logs -f frontend
```

After the containers are running, visit:

- **Frontend (React)**: http://localhost:${FRONTEND_PORT}
- **Welcome Dashboard**: http://localhost:${WEB_PORT}/welcome.html

## Development Workflow

The application uses Vite's development server with Hot Module Replacement (HMR). Any changes you make to your React components will be instantly reflected in the browser without losing the current state.

### Key Files

- `src/App.tsx` - Main application component
- `src/main.tsx` - Application entry point
- `tailwind.config.js` - Tailwind CSS configuration
- `vite.config.ts` - Vite configuration
- `Dockerfile` - Container configuration

### Adding Dependencies

```bash
# Add a new dependency
docker compose exec frontend npm install axios

# Add a dev dependency
docker compose exec frontend npm install -D vitest
```

## Building for Production

The Dockerfile includes a build step that creates optimized production assets:

```bash
# Build production assets
docker compose build --no-cache
```

## Customizing

- Modify `tailwind.config.js` to customize your design system
- Update `vite.config.ts` to customize your build settings
- Edit `.env` to change environment variables

## Ports

- **Frontend (Dev Server)**: ${FRONTEND_PORT}
- **Nginx**: ${WEB_PORT}

Happy coding! 🚀
