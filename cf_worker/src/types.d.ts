import { VectorizeIndex } from '@cloudflare/workers-types'
import { KVNamespace } from '@cloudflare/workers-types';

declare module '*.html' {
  const content: string;
  export default content;
}

export interface Env {
  VECTORIZE_INDEX: VectorizeIndex
  __STATIC_CONTENT: KVNamespace
}

export interface ExtendedRequest extends Request {
  params?: Record<string, string>;
}

export interface RouterRequest extends ExtendedRequest {
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