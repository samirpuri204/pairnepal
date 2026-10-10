/* Live test of the PairNepal signalling endpoint.
   Connects two clients the same way the browser does, asks both to join the
   IP-based room, and reports whether each one sees the other.

   Usage: node ws-test.mjs [host]           (default: the Vercel deployment) */

import WebSocket from 'ws';

const host = process.argv[2] || 'public-peach-nu.vercel.app';
const proto = host.includes('localhost') ? 'ws' : 'wss';
const url = `${proto}://${host}/server?webrtc_supported=true`;

const seen = { A: [], B: [] };
let done = false;

function attach(label, name) {
    const ws = new WebSocket(url, { handshakeTimeout: 20000 });
    let opened = false;

    ws.on('open', () => {
        opened = true;
        console.log(`[${label}] open`);
        ws.send(JSON.stringify({ type: 'join-ip-room' }));
    });

    ws.on('message', (raw) => {
        let m;
        try { m = JSON.parse(raw.toString()); } catch { return; }
        const t = m.type;
        if (label === 'A') seen.A.push(t); else seen.B.push(t);
        if (t === 'display-name') console.log(`[${label}] display-name: ${m.displayName}`);
        else if (t === 'peer-joined') console.log(`[${label}] peer-joined: ${m.peer && m.peer.name ? m.peer.name.displayName : '?'}`);
        else console.log(`[${label}] ${t}`);
    });

    ws.on('error', (e) => console.log(`[${label}] error: ${e.message}`));
    ws.on('close', (code) => console.log(`[${label}] closed (${code})${opened ? '' : ' — never opened'}`));
    return ws;
}

console.log('Testing', url, '\n');
const a = attach('A');
setTimeout(() => attach('B'), 1500);

setTimeout(() => {
    const okUpgrade = seen.A.length > 0 && seen.B.length > 0;
    const mutual = seen.A.includes('peer-joined') && seen.B.includes('peer-joined');
    console.log('\n--- result ---');
    console.log('A saw:', seen.A.join(', ') || '(nothing)');
    console.log('B saw:', seen.B.join(', ') || '(nothing)');
    console.log('upgrade accepted by both:', okUpgrade);
    console.log('mutual peer discovery  :', mutual);
    console.log(mutual && okUpgrade ? 'PASS — signalling works' : 'FAIL');
    a.close(); process.exit(mutual && okUpgrade ? 0 : 1);
}, 9000);
