declare module 'itty-router' {
    export interface IRequest extends Request {
      params?: Record<string, string>
      query?: Record<string, string>
    }
  
    export interface RouterType {
      handle: (request: Request, ...args: any[]) => Promise<Response>
      get: (path: string, handler: RouteHandler) => RouterType
      post: (path: string, handler: RouteHandler) => RouterType
      put: (path: string, handler: RouteHandler) => RouterType
      delete: (path: string, handler: RouteHandler) => RouterType
      all: (path: string, handler: RouteHandler) => RouterType
    }
  
    export type RouteHandler = (request: IRequest, ...args: any[]) => Promise<Response> | Response
  
    export function Router(): RouterType
  }