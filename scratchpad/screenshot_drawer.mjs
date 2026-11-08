import { spawn } from 'child_process';
import fs from 'fs';

async function run() {
  const edgePath = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
  const edge = spawn(edgePath, [
    '--headless=new',
    '--remote-debugging-port=9222',
    '--disable-gpu',
    '--no-sandbox',
    '--window-size=1680,1050',
    'http://localhost:5173/'
  ]);

  try {
    let targets = null;
    for (let i = 0; i < 20; i++) {
      await new Promise(r => setTimeout(r, 500));
      try {
        const res = await fetch('http://127.0.0.1:9222/json');
        targets = await res.json();
        if (targets && targets.length > 0) break;
      } catch (e) {}
    }

    const pageTarget = targets.find(t => t.type === 'page');
    const ws = new WebSocket(pageTarget.webSocketDebuggerUrl);

    await new Promise((resolve) => ws.onopen = resolve);

    let id = 1;
    function send(method, params = {}) {
      return new Promise((resolve, reject) => {
        const msgId = id++;
        const handler = (evt) => {
          const msg = JSON.parse(evt.data);
          if (msg.id === msgId) {
            ws.removeEventListener('message', handler);
            resolve(msg.result);
          }
        };
        ws.addEventListener('message', handler);
        ws.send(JSON.stringify({ id: msgId, method, params }));
      });
    }

    await new Promise(r => setTimeout(r, 3000));

    // Click row with "MO Retry" (which has 667 Baseline badge)
    const clickRes = await send('Runtime.evaluate', {
      expression: `(() => {
        const rows = Array.from(document.querySelectorAll('tbody tr'));
        const verifiedRow = rows.find(r => r.innerText.includes('MO Retry') || r.innerText.includes('667 Baseline'));
        if (verifiedRow) {
          verifiedRow.click();
          return 'clicked verified row: ' + verifiedRow.innerText.slice(0, 40);
        }
        return 'not_found';
      })()`
    });
    console.log('Row click evaluation:', clickRes);

    await new Promise(r => setTimeout(r, 800));

    const screenshot = await send('Page.captureScreenshot', { format: 'png' });
    const buffer = Buffer.from(screenshot.data, 'base64');
    fs.writeFileSync('c:\\Users\\rahma\\OneDrive\\Documents\\worklens\\dashboard_drawer_verified.png', buffer);
    fs.writeFileSync('C:\\Users\\rahma\\.gemini\\antigravity\\brain\\1c91b011-3e75-410c-9186-2c10ea203ba7\\dashboard_drawer_verified.png', buffer);
    console.log('Saved dashboard_drawer_verified.png successfully, size:', buffer.length);

    ws.close();
  } finally {
    edge.kill();
  }
}

run().catch(console.error);
