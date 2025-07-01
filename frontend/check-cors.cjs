const { request } = require('@playwright/test');

(async () => {
  const apiUrl = 'https://chatbot-5avk.onrender.com/chat';

  // Preflight(OPTIONS) 요청
  const context = await request.newContext();
  const optionsRes = await context.fetch(apiUrl, {
    method: 'OPTIONS',
    headers: {
      'Origin': 'https://chatbot-1-uz5m.onrender.com',
      'Access-Control-Request-Method': 'POST',
      'Access-Control-Request-Headers': 'content-type'
    }
  });
  console.log('OPTIONS status:', optionsRes.status());
  console.log('OPTIONS headers:', optionsRes.headers());

  // 실제 POST 요청
  const postRes = await context.fetch(apiUrl, {
    method: 'POST',
    headers: {
      'Origin': 'https://chatbot-1-uz5m.onrender.com',
      'Content-Type': 'application/json'
    },
    data: JSON.stringify({ message: '안녕', model: 'claude-3.7-sonnet' })
  });
  console.log('POST status:', postRes.status());
  console.log('POST headers:', postRes.headers());

  await context.dispose();
})();