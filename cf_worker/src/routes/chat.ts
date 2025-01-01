import { Router } from 'itty-router'
import type { Env, ExtendedRequest } from '../types'
import { Request, Response, ExecutionContext } from '@cloudflare/workers-types';

async function embedQuestion(question: string): Promise<number[]> {
  // TODO: Replace with actual embedding implementation
  return new Array(1536).fill(0).map(() => Math.random())
}

function constructColbieResponse(question: string, searchResults: any[]): string {
  if (!searchResults.length) {
    return "Colbie: Beep boop! I'm sorry, I couldn't find any information about that. 🤖"
  }

  const relevantText = searchResults
    .map(result => result.metadata?.text || '')
    .filter(Boolean)
    .join('\n\n')

  return `Colbie: Beep boop! Here's what I found about "${question}":\n\n${relevantText} ✨`
}

export function setupChatRoutes(router: Router<Env>) {
  router.post('/chat', async (request: Request, env: Env) => {
    try {
      const { question } = await request.json() as { question: string }

      const questionEmbedding = await embedQuestion(question)
      const searchResults = await env.VECTORIZE.query(questionEmbedding, {
        topK: 3
      })

      const response = constructColbieResponse(question, searchResults)
      return Response.json({ response })
    } catch (error) {
      return Response.json({ error: error.message }, { status: 500 })
    }
  })
}