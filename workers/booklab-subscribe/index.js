// BookLab Newsletter Subscribe Worker
// Subscribes email to Beehiiv + notifies Discord

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const allowed = [env.ALLOWED_ORIGIN, 'http://localhost:8080', 'http://127.0.0.1:8080'];
    const corsOrigin = allowed.includes(origin) ? origin : env.ALLOWED_ORIGIN;
    const corsHeaders = {
      'Access-Control-Allow-Origin': corsOrigin,
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders });
    }
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405, headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    try {
      const body = await request.json();
      const email = (body.email || '').trim().toLowerCase();
      if (!email || !email.includes('@')) {
        return new Response(JSON.stringify({ error: 'Invalid email' }), {
          status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }

      const res = await fetch(
        `https://api.beehiiv.com/v2/publications/${env.BEEHIIV_PUB_ID}/subscriptions`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${env.BEEHIIV_API_KEY}`,
          },
          body: JSON.stringify({
            email,
            reactivate_existing: true,
            send_welcome_email: true,
            utm_source: body.utm_source || 'website',
            utm_medium: body.utm_medium || 'organic',
          }),
        }
      );

      const data = await res.json();

      if (res.ok) {
        // Notify Discord about new subscriber
        try {
          if (env.DISCORD_WEBHOOK_URL) {
            const country = request.headers.get('CF-IPCountry') || '??';
            await fetch(env.DISCORD_WEBHOOK_URL, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                embeds: [{
                  title: '📬 New Newsletter Subscriber!',
                  color: 0x57F287,
                  fields: [
                    { name: 'Email', value: email, inline: true },
                    { name: 'Country', value: country, inline: true },
                    { name: 'Source', value: `${body.utm_source || 'website'} / ${body.utm_medium || 'organic'}`, inline: true },
                  ],
                  timestamp: new Date().toISOString(),
                }],
              }),
            });
          }
        } catch (discordErr) {
          console.error('Discord webhook failed:', discordErr.message);
        }

        return new Response(JSON.stringify({ success: true }), {
          status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      } else {
        return new Response(JSON.stringify({ error: data.errors?.[0] || 'Subscription failed' }), {
          status: res.status, headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }
    } catch (err) {
      return new Response(JSON.stringify({ error: 'Server error' }), {
        status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }
  },
};
