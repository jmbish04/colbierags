import { Router } from 'itty-router'
import type { RouterType, RouterRequest } from '../types'
import type { Env } from '../types'
import visualizationTemplate from '../templates/visualization.html'

export function setupVisualizationRoutes(router: RouterType) {
  router.get('/visualize', async (request: RouterRequest, env: Env): Promise<Response> => {
    try {
      const indexDetails = await env.VECTORIZE_INDEX.describe()
      
      // Get vectors using query since we can't get them directly
      const results = await env.VECTORIZE_INDEX.query(
        Array(1536).fill(0), // dummy query vector
        { topK: 100 }
      )

      const visualData = results.matches.map(match => ({
        id: match.id,
        embedding: match.values,
        metadata: match.metadata
      }))

      const html = visualizationTemplate.replace(
        '// const vectorData = [...];',
        `const vectorData = ${JSON.stringify(visualData)};`
      )

      return new Response(html, {
        headers: {
          'Content-Type': 'text/html',
          'Cache-Control': 'no-cache'
        }
      })
    } catch (error) {
      console.error('Visualization error:', error)
      return Response.json({ error: error instanceof Error ? error.message : 'Unknown error' }, { status: 500 })
    }
  })
}