/* =============================================================================
   PairNepal — interface sound design
   -----------------------------------------------------------------------------
   Every cue is synthesised at runtime with the Web Audio API. No audio files are
   shipped, so there is nothing to licence, nothing to download, and the whole
   kit costs a few hundred bytes.

   Design intent (a "quiet instrument", not a slot machine):
     tick     12ms  hover feedback, barely perceptible
     click    70ms  button press
     found   220ms  a device appeared on the network (rising perfect fifth)
     notify  380ms  somebody wants to send you something (two-tone, gentle)
     send    520ms  a transfer left this device (filtered noise sweep)
     done    620ms  a transfer completed (warm triad)
     fault   240ms  something failed

   Rules:
   - AudioContext is created lazily on the first user gesture (browser policy).
   - Sound is OFF until the person opts in; the choice is persisted.
   - Nothing loops; every cue is one-shot and self-terminating.
   ========================================================================== */

(function () {
    'use strict';

    var STORAGE_KEY = 'pairnepal.sound';
    var ctx = null;
    var master = null;
    var enabled = false;
    var lastTick = 0;

    /* ---------------------------------------------------------------- helpers */

    function readPreference() {
        try { return localStorage.getItem(STORAGE_KEY) === 'on'; }
        catch (e) { return false; }
    }

    function writePreference(on) {
        try { localStorage.setItem(STORAGE_KEY, on ? 'on' : 'off'); }
        catch (e) { /* private mode — the session still works, just not remembered */ }
    }

    function ensureContext() {
        if (ctx) return ctx;
        var Ctor = window.AudioContext || window.webkitAudioContext;
        if (!Ctor) return null;
        ctx = new Ctor();
        master = ctx.createGain();
        master.gain.value = 0.5;          // conservative headroom
        master.connect(ctx.destination);
        return ctx;
    }

    /* A single sine/saw partial with an exponential decay envelope. */
    function tone(opts) {
        if (!enabled) return;
        var c = ensureContext();
        if (!c || c.state === 'suspended') return;

        var t0 = c.currentTime + (opts.delay || 0);
        var dur = opts.dur || 0.12;

        var osc = c.createOscillator();
        osc.type = opts.type || 'sine';
        osc.frequency.setValueAtTime(opts.from || 440, t0);
        if (opts.to && opts.to !== opts.from) {
            osc.frequency.exponentialRampToValueAtTime(opts.to, t0 + dur);
        }

        var g = c.createGain();
        var peak = (opts.gain == null ? 0.06 : opts.gain);
        g.gain.setValueAtTime(0.0001, t0);
        g.gain.exponentialRampToValueAtTime(peak, t0 + Math.min(0.02, dur * 0.25));
        g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);

        osc.connect(g);
        g.connect(master);
        osc.start(t0);
        osc.stop(t0 + dur + 0.02);
    }

    /* Filtered noise — used for the "something is moving" cues. */
    function noise(opts) {
        if (!enabled) return;
        var c = ensureContext();
        if (!c || c.state === 'suspended') return;

        var dur = opts.dur || 0.3;
        var t0 = c.currentTime + (opts.delay || 0);
        var frames = Math.max(1, Math.floor(c.sampleRate * dur));
        var buf = c.createBuffer(1, frames, c.sampleRate);
        var data = buf.getChannelData(0);
        for (var i = 0; i < frames; i++) {
            // fade the noise itself so there is no click at the edges
            var p = i / frames;
            data[i] = (Math.random() * 2 - 1) * (1 - p);
        }

        var src = c.createBufferSource();
        src.buffer = buf;

        var filter = c.createBiquadFilter();
        filter.type = opts.filter || 'bandpass';
        filter.frequency.setValueAtTime(opts.from || 500, t0);
        if (opts.to) filter.frequency.exponentialRampToValueAtTime(opts.to, t0 + dur);
        filter.Q.value = opts.q == null ? 0.9 : opts.q;

        var g = c.createGain();
        g.gain.setValueAtTime(0.0001, t0);
        g.gain.exponentialRampToValueAtTime(opts.gain == null ? 0.05 : opts.gain, t0 + 0.03);
        g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);

        src.connect(filter);
        filter.connect(g);
        g.connect(master);
        src.start(t0);
        src.stop(t0 + dur + 0.02);
    }

    /* ------------------------------------------------------------------ cues */

    var cues = {
        tick: function () {
            var now = performance.now();
            if (now - lastTick < 90) return;   // never machine-gun a hover
            lastTick = now;
            tone({ from: 2100, to: 1750, dur: 0.05, gain: 0.018, type: 'sine' });
        },

        click: function () {
            tone({ from: 720, to: 520, dur: 0.07, gain: 0.05, type: 'triangle' });
        },

        found: function () {
            // rising perfect fifth — "something arrived"
            tone({ from: 523.25, dur: 0.16, gain: 0.05 });
            tone({ from: 783.99, dur: 0.22, gain: 0.045, delay: 0.09 });
        },

        notify: function () {
            // gentle two-tone, deliberately not an alarm
            tone({ from: 659.25, dur: 0.18, gain: 0.055 });
            tone({ from: 880.0, dur: 0.26, gain: 0.05, delay: 0.13 });
        },

        send: function () {
            noise({ from: 380, to: 2400, dur: 0.42, gain: 0.05, q: 0.7 });
            tone({ from: 392, to: 587.33, dur: 0.34, gain: 0.035, delay: 0.05 });
        },

        done: function () {
            // warm major triad, arpeggiated
            tone({ from: 523.25, dur: 0.4, gain: 0.05 });
            tone({ from: 659.25, dur: 0.45, gain: 0.045, delay: 0.07 });
            tone({ from: 783.99, dur: 0.55, gain: 0.05, delay: 0.14 });
        },

        fault: function () {
            tone({ from: 220, to: 165, dur: 0.2, gain: 0.05, type: 'triangle' });
        }
    };

    /* ------------------------------------------------------------------- API */

    var api = {
        /** Play a named cue. Unknown names are ignored rather than thrown. */
        play: function (name) {
            var fn = cues[name];
            if (fn) fn();
        },

        isEnabled: function () { return enabled; },

        setEnabled: function (on) {
            enabled = !!on;
            writePreference(enabled);
            if (enabled) {
                var c = ensureContext();
                if (c && c.state === 'suspended') c.resume();
                // confirm the choice audibly
                cues.found();
            }
            syncButtons();
        },

        toggle: function () { api.setEnabled(!enabled); },

        /** Build the toggle button that the header uses. */
        button: function () {
            var b = document.createElement('div');
            b.className = 'icon-button pn-sound';
            b.setAttribute('role', 'button');
            b.setAttribute('tabindex', '0');
            b.setAttribute('aria-pressed', 'false');
            b.innerHTML =
                '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
                'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
                '<path d="M11 5 6.5 9H3v6h3.5L11 19z"/>' +
                '<g class="pn-sound__waves"><path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M18.5 6a9 9 0 0 1 0 12"/></g>' +
                '<g class="pn-sound__muted"><path d="M16 9.5l5 5"/><path d="M21 9.5l-5 5"/></g>' +
                '</svg>';
            // Create it already reflecting the stored preference. Syncing later
            // would leave the control showing the wrong state until first click.
            b.setAttribute('aria-pressed', enabled ? 'true' : 'false');
            b.title = enabled ? 'Interface sounds on' : 'Interface sounds off';
            b.setAttribute('aria-label', 'Toggle interface sounds');

            function activate() { api.toggle(); }
            b.addEventListener('click', activate);
            b.addEventListener('keydown', function (e) {
                if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); activate(); }
            });
            return b;
        },

        /** Attach the cues to the app's own DOM without touching its code. */
        bindToApp: function () {
            // Buttons — press feedback.
            document.addEventListener('pointerdown', function (e) {
                var t = e.target;
                if (t && t.closest && t.closest('.btn, .icon-button, x-peer')) {
                    if (t.closest('.pn-sound')) return;   // handled by the toggle itself
                    cues.click();
                }
            }, { passive: true });

            // Peers — a whisper of feedback on hover.
            document.addEventListener('pointerover', function (e) {
                var t = e.target;
                if (t && t.closest && t.closest('x-peer')) cues.tick();
            }, { passive: true });

            // New device on the network: watch the peer container for additions.
            var peers = document.querySelector('x-peers');
            if (peers && window.MutationObserver) {
                var seen = false;
                new MutationObserver(function (records) {
                    for (var i = 0; i < records.length; i++) {
                        if (records[i].addedNodes.length) {
                            // skip the initial hydration pass
                            if (seen) cues.found();
                            else seen = true;
                            return;
                        }
                    }
                }).observe(peers, { childList: true });
            }
        }
    };

    function syncButtons() {
        var all = document.querySelectorAll('.pn-sound');
        for (var i = 0; i < all.length; i++) {
            all[i].setAttribute('aria-pressed', enabled ? 'true' : 'false');
            all[i].setAttribute('title', enabled ? 'Interface sounds on' : 'Interface sounds off');
        }
    }

    // Any first gesture unlocks the context for the rest of the session.
    ['pointerdown', 'keydown'].forEach(function (evt) {
        window.addEventListener(evt, function once() {
            if (enabled) {
                var c = ensureContext();
                if (c && c.state === 'suspended') c.resume();
            }
            window.removeEventListener(evt, once);
        }, { passive: true });
    });

    enabled = readPreference();

    window.PairNepalSound = api;
})();
