import { Router } from 'itty-router'
import type { RouterType, IRequest } from 'itty-router'
import type { Env } from '../types'
import type { VectorizeVector, VectorizeVectorMetadata } from '@cloudflare/workers-types'

export function setupVectorRoutes(router: RouterType) {
  router.post('/add-vectors', async (request: IRequest, env: Env): Promise<Response> => {
    try {
      const { documents, embeddings, metadatas, ids } = await request.json() as {
        documents: string[]
        embeddings: number[][]
        metadatas?: Record<string, VectorizeVectorMetadata>[]
        ids?: string[]
      }

      const vectors: VectorizeVector[] = embeddings.map((embedding, i) => ({
        id: ids?.[i] ?? `doc_${i}`,
        values: embedding,
        metadata: {
          text: documents[i] as VectorizeVectorMetadata,
          ...(metadatas?.[i] ?? {})
        }
      }))

      await env.VECTORIZE_INDEX.insert(vectors)  // Changed from upsert to insert
      return Response.json({ success: true })
    } catch (error) {
      return Response.json({ error: error instanceof Error ? error.message : 'Unknown error' }, { status: 500 })
    }
  })

  router.post('/query', async (request: IRequest, env: Env): Promise<Response> => {
    try {
      const { query_embedding, n_results = 10, filter } = await request.json() as {
        query_embedding: number[]
        n_results?: number
        filter?: Record<string, any>
      }

      const results = await env.VECTORIZE_INDEX.query(query_embedding, {
        topK: n_results,
        filter
      })

      return Response.json(results)
    } catch (error) {
      return Response.json({ error: error instanceof Error ? error.message : 'Unknown error' }, { status: 500 })
    }
  })

  router.delete('/delete', async (request: IRequest, env: Env): Promise<Response> => {
    try {
      const { ids } = await request.json() as { ids: string[] }
      await env.VECTORIZE_INDEX.deleteByIds(ids)  // Changed from delete to deleteByIds
      return Response.json({ success: true })
    } catch (error) {
      return Response.json({ error: error instanceof Error ? error.message : 'Unknown error' }, { status: 500 })
    }
  })

  router.post('/get-vectors', async (request: IRequest, env: Env): Promise<Response> => {
    try {
      const { ids, where, limit, offset } = await request.json() as {
        ids?: string[]
        where?: Record<string, any>
        limit?: number
        offset?: number
      }

      const results = await env.VECTORIZE_INDEX.getByIds(ids || [])  // Changed to getByIds
      return Response.json(results)
    } catch (error) {
      return Response.json({ error: error instanceof Error ? error.message : 'Unknown error' }, { status: 500 })
    }
  })

  router.put('/update-vectors', async (request: IRequest, env: Env): Promise<Response> => {
    try {
      const { ids, documents, embeddings, metadatas } = await request.json() as {
        ids: string[]
        documents?: string[]
        embeddings: number[][]  // Make this required
        metadatas?: Record<string, VectorizeVectorMetadata>[]
      }
  
      // Only create vectors where we have valid embeddings
      const updates: VectorizeVector[] = ids.reduce<VectorizeVector[]>((acc, id, i) => {
        if (embeddings[i]) {  // Check if we have a valid embedding
          acc.push({
            id,
            values: embeddings[i],
            metadata: {
              text: documents?.[i] as VectorizeVectorMetadata,
              ...(metadatas?.[i] ?? {})
            }
          })
        }
        return acc
      }, [])
  
      if (updates.length === 0) {
        return Response.json({ error: 'No valid vectors to update' }, { status: 400 })
      }
  
      await env.VECTORIZE_INDEX.upsert(updates)
      return Response.json({ success: true, updated: updates.length })
    } catch (error) {
      return Response.json({ error: error instanceof Error ? error.message : 'Unknown error' }, { status: 500 })
    }
  })

  router.get('/peek', async (request: IRequest, env: Env): Promise<Response> => {
    try {
      const url = new URL(request.url)
      const n = parseInt(url.searchParams.get('n') || '10')
      const results = await env.VECTORIZE_INDEX.describe()  // Changed to describe()
      return Response.json(results)
    } catch (error) {
      return Response.json({ error: error instanceof Error ? error.message : 'Unknown error' }, { status: 500 })
    }
  })
}