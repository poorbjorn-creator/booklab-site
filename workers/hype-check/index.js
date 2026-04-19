/**
 * BookLab Hype Check — Cloudflare Worker + KV
 * 
 * Reusable voting backend for monthly book releases.
 * Each "edition" (e.g. "may-2026") has its own set of books.
 * Votes are deduplicated per visitor using IP + User-Agent hash.
 * 
 * KV keys:
 *   votes:{editionId}:{bookId}        → JSON { preorder: N, curious: N, notforme: N }
 *   voter:{editionId}:{bookId}:{hash}  → "1" (TTL 180 days)
 * 
 * Endpoints:
 *   GET  /votes?edition=may-2026&book=1       → get vote counts for one book
 *   GET  /votes?edition=may-2026              → get all votes for an edition
 *   POST /vote  { edition, book, choice }     → cast a vote
 *   GET  /stats?edition=may-2026              → admin stats
 */

const VALID_CHOICES = ['preorder', 'curious', 'notforme'];

function corsHeaders(origin, env) {
  const allowed = (env.ALLOWED_ORIGINS || '').split(',').map(s => s.trim());
  const allow = allowed.includes(origin) ? origin : allowed[0] || '*';
  return {
    'Access-Control-Allow-Origin': allow,
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
  };
}

async function hashVoter(request) {
  const ip = request.headers.get('CF-Connecting-IP') || request.headers.get('X-Forwarded-For') || 'unknown';
  const ua = request.headers.get('User-Agent') || 'unknown';
  const raw = `${ip}::${ua}`;
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(raw));
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('').slice(0, 16);
}

async function getVotes(kv, edition, bookId) {
  const key = `votes:${edition}:${bookId}`;
  const data = await kv.get(key, 'json');
  return data || { preorder: 0, curious: 0, notforme: 0 };
}

async function getAllVotes(kv, edition) {
  const list = await kv.list({ prefix: `votes:${edition}:` });
  const results = {};
  for (const key of list.keys) {
    const bookId = key.name.split(':')[2];
    const data = await kv.get(key.name, 'json');
    results[bookId] = data || { preorder: 0, curious: 0, notforme: 0 };
  }
  return results;
}

async function handleVote(request, env) {
  let body;
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ error: 'Invalid JSON' }), { status: 400 });
  }

  const { edition, book, choice } = body;
  if (!edition || !book || !choice) {
    return new Response(JSON.stringify({ error: 'Missing edition, book, or choice' }), { status: 400 });
  }
  if (!VALID_CHOICES.includes(choice)) {
    return new Response(JSON.stringify({ error: 'Invalid choice' }), { status: 400 });
  }
  // Sanitize inputs
  const editionId = String(edition).replace(/[^a-z0-9-]/g, '').slice(0, 20);
  const bookId = String(book).replace(/[^a-z0-9-]/g, '').slice(0, 30);

  const voterHash = await hashVoter(request);
  const voterKey = `voter:${editionId}:${bookId}:${voterHash}`;

  // Check if already voted
  const existing = await env.HYPE_VOTES.get(voterKey);
  if (existing) {
    // Return current votes without adding
    const votes = await getVotes(env.HYPE_VOTES, editionId, bookId);
    return new Response(JSON.stringify({ ok: true, already_voted: true, votes }), {
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // Record vote
  const votesKey = `votes:${editionId}:${bookId}`;
  const current = await getVotes(env.HYPE_VOTES, editionId, bookId);
  current[choice] = (current[choice] || 0) + 1;
  
  await env.HYPE_VOTES.put(votesKey, JSON.stringify(current));
  await env.HYPE_VOTES.put(voterKey, '1', { expirationTtl: 180 * 86400 }); // 180 days

  return new Response(JSON.stringify({ ok: true, votes: current }), {
    headers: { 'Content-Type': 'application/json' },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origin = request.headers.get('Origin') || '';
    const cors = corsHeaders(origin, env);

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: cors });
    }

    let response;

    try {
      if (url.pathname === '/vote' && request.method === 'POST') {
        response = await handleVote(request, env);
      } else if (url.pathname === '/votes' && request.method === 'GET') {
        const edition = url.searchParams.get('edition');
        const book = url.searchParams.get('book');
        if (!edition) {
          response = new Response(JSON.stringify({ error: 'Missing edition' }), { status: 400 });
        } else if (book) {
          const votes = await getVotes(env.HYPE_VOTES, edition, book);
          // Also check if this visitor already voted
          const voterHash = await hashVoter(request);
          const voterKey = `voter:${edition}:${book}:${voterHash}`;
          const voted = await env.HYPE_VOTES.get(voterKey);
          response = new Response(JSON.stringify({ votes, voted: !!voted }), {
            headers: { 'Content-Type': 'application/json' },
          });
        } else {
          const all = await getAllVotes(env.HYPE_VOTES, edition);
          // Check voter status for all books
          const voterHash = await hashVoter(request);
          const voterStatus = {};
          for (const bookId of Object.keys(all)) {
            const vk = `voter:${edition}:${bookId}:${voterHash}`;
            voterStatus[bookId] = !!(await env.HYPE_VOTES.get(vk));
          }
          response = new Response(JSON.stringify({ votes: all, voted: voterStatus }), {
            headers: { 'Content-Type': 'application/json' },
          });
        }
      } else if (url.pathname === '/stats' && request.method === 'GET') {
        const edition = url.searchParams.get('edition');
        if (!edition) {
          response = new Response(JSON.stringify({ error: 'Missing edition' }), { status: 400 });
        } else {
          const all = await getAllVotes(env.HYPE_VOTES, edition);
          let totalVotes = 0;
          for (const bookVotes of Object.values(all)) {
            totalVotes += (bookVotes.preorder || 0) + (bookVotes.curious || 0) + (bookVotes.notforme || 0);
          }
          response = new Response(JSON.stringify({ edition, books: Object.keys(all).length, totalVotes, data: all }), {
            headers: { 'Content-Type': 'application/json' },
          });
        }
      } else {
        response = new Response(JSON.stringify({ service: 'BookLab Hype Check', version: '1.0' }), {
          headers: { 'Content-Type': 'application/json' },
        });
      }
    } catch (err) {
      response = new Response(JSON.stringify({ error: 'Internal error' }), { status: 500 });
    }

    // Apply CORS headers
    const newHeaders = new Headers(response.headers);
    for (const [k, v] of Object.entries(cors)) {
      newHeaders.set(k, v);
    }
    newHeaders.set('Content-Type', 'application/json');

    return new Response(response.body, {
      status: response.status,
      headers: newHeaders,
    });
  },
};
