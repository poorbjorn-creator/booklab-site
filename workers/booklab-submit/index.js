// BookLab Book Submission Worker
// Receives submissions from submit-book.html, stores in KV, notifies via email

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': 'https://booklabbybjorn.com',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS_HEADERS });
    }

    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405, headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' }
      });
    }

    try {
      const data = await request.json();

      // Validate required fields
      if (!data.title || !data.author || !data.pubDate || !data.category || !data.pitch) {
        return new Response(JSON.stringify({ error: 'Missing required fields' }), {
          status: 400, headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' }
        });
      }

      // Add metadata
      const submission = {
        ...data,
        submittedAt: new Date().toISOString(),
        ip: request.headers.get('CF-Connecting-IP') || 'unknown',
        country: request.headers.get('CF-IPCountry') || 'unknown',
      };

      // Store in KV
      const key = `submission:${Date.now()}:${data.title.slice(0, 30).replace(/\s+/g, '-')}`;
      let kvStored = false;
      try {
        if (env.SUBMISSIONS) {
          await env.SUBMISSIONS.put(key, JSON.stringify(submission), { expirationTtl: 365 * 86400 });
          kvStored = true;
        }
      } catch (kvErr) {
        console.error('KV write failed:', kvErr.message);
      }

      // Post to Discord via webhook
      try {
        const discordPayload = {
          embeds: [{
            title: `📚 New Book Submission`,
            color: 0x5865F2,
            fields: [
              { name: 'Title', value: submission.title, inline: true },
              { name: 'Author', value: submission.author, inline: true },
              { name: 'Category', value: submission.category, inline: true },
              { name: 'Pub Date', value: submission.pubDate, inline: true },
              { name: 'Publisher', value: submission.publisher || 'N/A', inline: true },
              { name: 'Country', value: submission.country || 'N/A', inline: true },
              { name: 'Pitch', value: (submission.pitch || '').slice(0, 1024) || 'N/A' },
              { name: 'Link', value: submission.link || 'N/A' },
              { name: 'Submitted By', value: `${submission.submitterName || 'Anonymous'} (${submission.submitterRole || 'unknown'})` },
              { name: 'Email', value: submission.submitterEmail || 'N/A', inline: true },
            ],
            timestamp: submission.submittedAt,
          }],
        };
        if (env.DISCORD_WEBHOOK_URL) {
          await fetch(env.DISCORD_WEBHOOK_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(discordPayload),
          });
        }
      } catch (discordErr) {
        console.error('Discord webhook failed:', discordErr.message);
      }

      console.log('New book submission:', JSON.stringify(submission), 'KV stored:', kvStored);

      return new Response(JSON.stringify({ ok: true, message: 'Submission received', kvStored }), {
        status: 200, headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' }
      });

    } catch (err) {
      return new Response(JSON.stringify({ error: 'Invalid request' }), {
        status: 400, headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' }
      });
    }
  }
};
