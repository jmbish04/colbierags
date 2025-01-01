import { VectorizeIndex } from '@cloudflare/workers-types'

export interface Env {
  VECTORIZE_INDEX: VectorizeIndex
  __STATIC_CONTENT: KVNamespace
}

// Define router types
export interface RouterRequest extends Request {
  params?: Record<string, string>
}

export interface RouterType {
  get: (path: string, handler: RouteHandler) => RouterType
  post: (path: string, handler: RouteHandler) => RouterType
  put: (path: string, handler: RouteHandler) => RouterType
  delete: (path: string, handler: RouteHandler) => RouterType
  all: (path: string, handler: RouteHandler) => RouterType
  handle: (request: Request, ...args: any[]) => Promise<Response>
}

export type RouteHandler = (request: RouterRequest, ...args: any[]) => Promise<Response> | Response