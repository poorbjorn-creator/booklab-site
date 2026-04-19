// BookLab Events Logger — lightweight tool usage tracker
// Stores daily event counts in KV: events:YYYY-MM-DD:{event_name}

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': 'https://booklabai.com',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

// Also allow booklabbybjorn.com
function corsHeaders(origin) {
  const allowed = ['https://booklabai.com', 'https://booklabbybjorn.com'];
  const o = allowed.includes(origin) ? origin : '*';
  return { ...CORS_HEADERS, 'Access-Control-Allow-Origin': o };
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const headers = corsHeaders(origin);

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers });
    }

    const url = new URL(request.url);

    // POST /track — log an event
    if (request.method === 'POST' && url.pathname === '/track') {
      try {
        const body = await request.json();
        const event = String(body.event || '').slice(0, 64);
        const page = String(body.page || '/').slice(0, 128);
        if (!event) return new Response('{"error":"missing event"}', { status: 400, headers });

        const today = new Date().toISOString().slice(0, 10);
        const key = `events:${today}:${event}`;
        const pageKey = `pages:${today}:${page}`;

        // Increment event count
        const current = parseInt(await env.EVENTS.get(key) || '0', 10);
        await env.EVENTS.put(key, String(current + 1), { expirationTtl: 90 * 86400 }); // 90 day TTL

        // Increment page count
        const pageCurrent = parseInt(await env.EVENTS.get(pageKey) || '0', 10);
        await env.EVENTS.put(pageKey, String(pageCurrent + 1), { expirationTtl: 90 * 86400 });

        return new Response('{"ok":true}', { headers: { ...headers, 'Content-Type': 'application/json' } });
      } catch (e) {
        return new Response('{"error":"bad request"}', { status: 400, headers });
      }
    }

    // GET /stats?days=7 — read recent stats (for Alfred to query)
    if (request.method === 'GET' && url.pathname === '/stats') {
      const days = Math.min(parseInt(url.searchParams.get('days') || '7', 10), 90);
      const result = {};

      for (let i = 0; i < days; i++) {
        const d = new Date(Date.now() - i * 86400000).toISOString().slice(0, 10);
        const list = await env.EVENTS.list({ prefix: `events:${d}:` });
        const pageList = await env.EVENTS.list({ prefix: `pages:${d}:` });

        const events = {};
        for (const key of list.keys) {
          const name = key.name.replace(`events:${d}:`, '');
          events[name] = parseInt(await env.EVENTS.get(key.name) || '0', 10);
        }

        const pages = {};
        for (const key of pageList.keys) {
          const name = key.name.replace(`pages:${d}:`, '');
          pages[name] = parseInt(await env.EVENTS.get(key.name) || '0', 10);
        }

        if (Object.keys(events).length || Object.keys(pages).length) {
          result[d] = { events, pages };
        }
      }

      return new Response(JSON.stringify(result, null, 2), {
        headers: { ...headers, 'Content-Type': 'application/json' },
      });
    }

    return new Response('BookLab Events API', { headers });
  },
};
