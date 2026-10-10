/* Live test of the PairNepal signalling endpoint.

   PairDrop's protocol is asymmetric, which an earlier version of this test got
   wrong: the peer that joins an existing room receives the roster in a `peers`
   message, while peers already in the room receive `peer-joined`. Mutual
   discovery therefore means:

       first client in   -> receives `peer-joined` for the second
       second client in  -> receives `peers` containing the first

   Usage: node ws-test.mjs [host] */

import WebSocket from 'ws';

const host = process.argv[2] || 'public-peach-nu.vercel.app';
const proto = host.includes('localhost') ? 'ws' : 'wss';
const url = `${proto}://${host}/server?webrtc_supported=true`;

const state = {
    A: { types: [], instanceId: null, selfId: null, selfName: null, roster: [], peerJoined: [] },
    B: { types: [], instanceId: null, selfId: null, selfName: null, roster: [], peerJoined: [] }
};

function attach(label) {
    const ws = new WebSocket(url, { handshakeTimeout: 20000 });
    const s = state[label];

    ws.on('open', () => {
        console.log(`[${label}] upgrade accepted`);
        ws.send(JSON.stringify({ type: 'join-ip-room' }));
    });

    ws.on('message', (raw) => {
        let m;
        try { m = JSON.parse(raw.toString()); } catch { return; }
        s.types.push(m.type);

        if (m.type === 'ws-config') {
            s.instanceId = m.instanceId || '(none)';
            console.log('[' + label + '] instance: ' + s.instanceId);
        }
        if (m.type === 'display-name') {
            s.selfId = m.peerId;
            s.selfName = m.displayName;
            console.log(`[${label}] my name is "${m.displayName}" id=${String(m.peerId).slice(0, 12)}…`);
        }
        if (m.type === 'peers') {
            s.roster = (m.peers || []).map((p) => p.name || p.id);
            console.log(`[${label}] roster received: ${JSON.stringify(s.roster)}`);
        }
        if (m.type === 'peer-joined') {
            const name = m.peer && m.peer.name ? m.peer.name.displayName : m.peer && m.peer.id;
            s.peerJoined.push(name);
            console.log(`[${label}] peer-joined: ${name}`);
        }
    });

    ws.on('error', (e) => console.log(`[${label}] socket error: ${e.message}`));
    return ws;
}

console.log('Testing', url, '\n');
const a = attach('A');

setTimeout(() => attach('B'), 2000);

setTimeout(() => {
    const A = state.A, B = state.B;
    const upgradeOk = A.types.length > 0 && B.types.length > 0;

    // A joined first, so B must appear to A as a join; B must see A in its roster.
    const aSeesB = A.peerJoined.length > 0;
    const bSeesA = B.roster.length > 0;

    console.log('\n--- result ---');
    console.log('A types :', A.types.join(', '));
    console.log('B types :', B.types.join(', '));
    console.log(`A "${A.selfName}" saw peer-joined for:', ${JSON.stringify(A.peerJoined)}`);
    console.log(`B "${B.selfName}" roster:', ${JSON.stringify(B.roster)}`);
    console.log('');
    console.log('upgrade accepted by both :', upgradeOk);
    console.log('first client saw the join:', aSeesB);
    console.log('joiner saw the roster   :', bSeesA);

    const pass = upgradeOk && aSeesB && bSeesA;
    console.log(pass ? '\nPASS — mutual peer discovery over the live signalling server' : '\nFAIL');
    process.exit(pass ? 0 : 1);
}, 12000);
