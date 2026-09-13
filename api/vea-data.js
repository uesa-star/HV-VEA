module.exports = async function handler(req, res) {
  if (req.method !== 'GET') {
    res.setHeader('Allow', 'GET');
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  const allowed = new Set(['edas', 'iras', 'febriles', 'individual']);
  const table = String(req.query.table || '').toLowerCase();
  if (!allowed.has(table)) {
    return res.status(400).json({ error: 'Tabla no permitida' });
  }

  const rawOffset = Number.parseInt(String(req.query.offset || '0'), 10);
  const rawLimit = Number.parseInt(String(req.query.limit || '300'), 10);
  const offset = Number.isFinite(rawOffset) && rawOffset >= 0 ? rawOffset : 0;
  const limit = Number.isFinite(rawLimit) ? Math.max(1, Math.min(rawLimit, 500)) : 300;

  const apikey = req.headers.apikey;
  const authorization = req.headers.authorization;
  if (!apikey || !authorization) {
    return res.status(401).json({ error: 'Credenciales públicas faltantes' });
  }

  const upstreamUrl = `https://qtsfkoasfoaovadilwgk.supabase.co/rest/v1/${encodeURIComponent(table)}?select=*&offset=${offset}&limit=${limit}`;

  try {
    const upstream = await fetch(upstreamUrl, {
      method: 'GET',
      headers: {
        apikey,
        Authorization: authorization,
        Accept: 'application/json'
      },
      cache: 'no-store'
    });

    const body = await upstream.text();
    res.setHeader('Cache-Control', 'no-store, max-age=0');
    res.setHeader('Content-Type', upstream.headers.get('content-type') || 'application/json; charset=utf-8');
    return res.status(upstream.status).send(body);
  } catch (err) {
    return res.status(502).json({ error: 'No se pudo consultar Supabase', detail: String(err?.message || err) });
  }
};
