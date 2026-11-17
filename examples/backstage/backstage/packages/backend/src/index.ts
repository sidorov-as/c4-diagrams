import { createBackend } from '@backstage/backend-defaults';

const backend = createBackend();

// Serves the frontend bundle
backend.add(import('@backstage/plugin-app-backend'));

// Auth: guest provider for the UI (see app-config.demo.yaml for service tokens)
backend.add(import('@backstage/plugin-auth-backend'));
backend.add(import('@backstage/plugin-auth-backend-module-guest-provider'));

// Catalog
backend.add(import('@backstage/plugin-catalog-backend'));
backend.add(import('@backstage/plugin-catalog-backend-module-logs'));

// Permissions: allow everything (local demo only)
backend.add(import('@backstage/plugin-permission-backend'));
backend.add(
  import('@backstage/plugin-permission-backend-module-allow-all-policy'),
);

backend.start();
