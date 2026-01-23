export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const { action, username, password, token, userId } = req.body || {};

  try {
    if (action === 'login') {
      const response = await fetch('https://web.spaggiari.eu/rest/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Z-Dev-Apikey': 'Tg1NWEwNGIgIC0K',
          'User-Agent': 'CVVS/std/4.2.3 Android/12',
        },
        body: JSON.stringify({ ident: null, pass: password, uid: username })
      });
      const data = await response.json();
      
      if (response.ok) {
        const rawIdent = data.ident || '';
        const numericUserId = rawIdent.replace(/[^0-9]/g, '');
        
        return res.status(200).json({
          token: data.token,
          userId: numericUserId
        });
      } else {
        return res.status(response.status).json({ error: 'Login failed' });
      }
    }

    if (action === 'carta') {
      const response = await fetch(`https://web.spaggiari.eu/rest/v1/students/${userId}/card`, {
        method: 'GET',
        headers: {
          'Z-Dev-Apikey': 'Tg1NWEwNGIgIC0K',
          'Z-Auth-Token': token,
          'User-Agent': 'CVVS/std/4.2.3 Android/12',
        }
      });
      const data = await response.json();
      return res.status(200).json(data.card || {});
    }

    if (action === 'voti') {
      const response = await fetch(`https://web.spaggiari.eu/rest/v1/students/${userId}/grades`, {
        method: 'GET',
        headers: {
          'Z-Dev-Apikey': 'Tg1NWEwNGIgIC0K',
          'Z-Auth-Token': token,
          'User-Agent': 'CVVS/std/4.2.3 Android/12',
        }
      });
      const data = await response.json();
      return res.status(200).json(data.grades || []);
    }

    if (action === 'assenze') {
      const response = await fetch(`https://web.spaggiari.eu/rest/v1/students/${userId}/absences/details`, {
        method: 'GET',
        headers: {
          'Z-Dev-Apikey': 'Tg1NWEwNGIgIC0K',
          'Z-Auth-Token': token,
          'User-Agent': 'CVVS/std/4.2.3 Android/12',
        }
      });
      const data = await response.json();
      return res.status(200).json(data.events || []);
    }

    return res.status(400).json({ error: 'Invalid action' });
    
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
}
