import { Router } from 'itty-router'
import { setupVectorRoutes } from './routes/vectors'
import { setupVisualizationRoutes } from './routes/visualize'
import { Request, Response, ExecutionContext } from '@cloudflare/workers-types';
import type { Env } from './types'

// Create router instance
const router = Router()

// Register routes once during initialization
setupVectorRoutes(router)
setupVisualizationRoutes(router)

// Function to convert a Request to RequestLike
function toRequestLike(request: Request): RequestLike {
  return {
    url: request.url,
    ...request // Spread the rest of the properties, including method
  };
}

// Export the fetch handler
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    // Convert request to RequestLike
    const requestLike = toRequestLike(request);
    return router.handle(requestLike, env, ctx) as unknown as Response;
  }
}