/* =============================================================================
   PairNepal signalling server — Vercel Function
   -----------------------------------------------------------------------------
   Vercel Functions serve WebSocket connections natively (public beta, all plans)
   when a Node function exports an `http.Server`. Vercel performs the HTTP Upgrade
   itself, so this file only has to build the server and attach the WebSocket
   server — it must never call listen().

   How a client reaches it:
       client  ->  wss://<host>/server
       vercel.json rewrites /server -> /api/server   (rewrites are applied to the
       upgrade request before it reaches the function)

   The protocol, peer registry and room logic are the app's own modules, reused
   unchanged from ../pn-lib (copied from server/ by sync-vercel-fn.py). No
   upstream signalling behaviour has been reimplemented here.

   Deployment notes that affect behaviour:
   - A connection is pinned to one function instance for its lifetime, and
     closes when the instance reaches its maximum duration. The browser client
     already reconnects, and in-flight file transfers run over WebRTC data
     channels rather than this socket, so a reconnect does not interrupt a
     transfer.
   - Two clients can, in principle, land on different instances and then not see
     each other. Vercel's guidance for that is an external store. For a small
     deployment a single warm instance is the normal case.
   - Peer grouping is by client IP, and Peer reads it from x-forwarded-for,
     which Vercel populates with the real client address. So "on this network"
     still means the same public IP, not Vercel's internal address.
   ========================================================================== */

import http from 'http';
import crypto from 'crypto';
import PairDropWsServer from '../pn-lib/ws-server.js';

/* Identifies the process serving a connection. Two peers can only discover each
   other when they land on the same one, so surfacing it makes that verifiable
   from the outside instead of guessed at. */
const INSTANCE_ID = crypto.randomUUID().slice(0, 8);

/* Mirrors the defaults built in server/index.js, minus the process.exit paths
   (a serverless invocation must never exit the process). */
const conf = {
    debugMode: false,
    port: 0,                 // never used: Vercel owns the listener
    wsFallback: false,       // WebRTC carries file data; no relay needed
    rtcConfig: {
        sdpSemantics: 'unified-plan',
        iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
    },
    signalingServer: false,  // this instance *is* the signalling server
    ipv6Localize: false,
    rateLimit: false
};

const server = http.createServer((req, res) => {
    // Plain HTTP on the same path is a liveness probe. It reports how many
    // sockets this instance is holding, which is the only way to observe the
    // peer registry from outside.
    const peers = pairDropWsServer && pairDropWsServer._wss
        ? pairDropWsServer._wss.clients.size
        : 0;
    const rooms = pairDropWsServer && pairDropWsServer._rooms
        ? Object.keys(pairDropWsServer._rooms).filter((k) => (pairDropWsServer._rooms[k] || []).length).length
        : 0;

    res.writeHead(200, {
        'Content-Type': 'application/json; charset=utf-8',
        'Cache-Control': 'no-store'
    });
    res.end(JSON.stringify({
        ok: true,
        service: 'pairnepal-signalling',
        instanceId: INSTANCE_ID,
        peers: peers,
        rooms: rooms,
        uptimeSeconds: Math.round(process.uptime())
    }));
});

// Module scope: survives across invocations on a warm instance, which is what
// keeps the peer registry alive for the lifetime of that instance.
const pairDropWsServer = new PairDropWsServer(server, conf);

/* Additive only: tag the handshake with the serving instance. Wrapping _send
   here keeps pn-lib a verbatim copy of the upstream modules. */
const sendToPeer = pairDropWsServer._send.bind(pairDropWsServer);
pairDropWsServer._send = (peer, message) => {
    if (message && message.type === 'ws-config') message.instanceId = INSTANCE_ID;
    return sendToPeer(peer, message);
};

export default server;
