// auth.js
const axios = require('axios');
require('dotenv').config();

async function getAccessToken() {
  if (process.env.USE_MOCK_AUTH === 'true') {
    // Simulate a fake JWT token
    const fakeToken = [
      Buffer.from(JSON.stringify({ alg: 'none', typ: 'JWT' })).toString('base64'),
      Buffer.from(JSON.stringify({
        aud: 'https://graph.microsoft.com',
        iss: 'https://login.microsoftonline.com/mocktenant/v2.0',
        exp: Math.floor(Date.now() / 1000) + 3600,
        name: 'Mock App',
        appid: 'mock-client-id'
      })).toString('base64'),
      ''
    ].join('.');
    console.log('authentication successful')
    return fakeToken;
  }

  const url = `https://login.microsoftonline.com/${process.env.TENANT_ID}/oauth2/v2.0/token`;
  const params = new URLSearchParams();
  params.append('grant_type', 'client_credentials');
  params.append('client_id', process.env.CLIENT_ID);
  params.append('client_secret', process.env.CLIENT_SECRET);
  params.append('scope', 'https://graph.microsoft.com/.default');

  try {
    const res = await axios.post(url, params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return res.data.access_token;
  } catch (err) {
    console.error('Failed to get token:', err.response?.data || err.message);
    return null;
  }
}

module.exports = { getAccessToken };
