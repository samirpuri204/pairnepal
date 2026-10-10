/* =============================================================================
   PairNepal — motion layer
   -----------------------------------------------------------------------------
   Four independent, opt-in behaviours. Each one degrades to "no animation, final
   state visible" if the browser lacks support or the visitor asked for reduced
   motion. Nothing here mutates app state or touches the app's own scripts.

     1. Magnetic      spring physics      (ported from 21st.dev "Magnetic", ibelick)
     2. CutReveal     vertical cut wipe  (ported from 21st.dev "Vertical Cut Reveal")
     3. Reveal        scroll entrances   (motion.csv patterns #4/#5/#7)
     4. Ident         brand motion graphic — animated SVG, no video file

   Performance contract (see research/CRAFT.md):
     - only `transform` and `opacity` are animated
     - every rAF loop has an explicit stop condition
     - pointer handlers never read layout on every move (rect is cached)
     - loops pause when the tab is hidden or the element leaves the viewport
   ========================================================================== */

(function () {
    'use strict';

    var reduceMotion = window.matchMedia &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Freeze every looping animation while the tab is hidden.
    document.addEventListener('visibilitychange', function () {
        document.body.classList.toggle('pn-idle', document.hidden);
    });

    /* =========================================================================
       1. Magnetic — ported spring physics
       Original: motion/react, x/y MotionValues driven by useSpring with
       SPRING_CONFIG { stiffness: 26.7, damping: 4.1, mass: 0.2 }, intensity .6,
       range 100px. Re-implemented as a plain integrator so it runs without a
       framework and writes only one composited property.
       ====================================================================== */
    function attachMagnetic(el, opts) {
        var o = opts || {};
        var intensity = o.intensity == null ? 0.6 : o.intensity;
        var range = o.range == null ? 100 : o.range;
        var stiffness = 26.7;
        var damping = 4.1;
        var mass = 0.2;

        var rect = null;
        var hovering = false;
        var raf = null;
        var x = 0, y = 0, vx = 0, vy = 0;
        var tx = 0, ty = 0;
        var last = 0;

        function measure() { rect = el.getBoundingClientRect(); }

        function step(now) {
            var dt = last ? Math.min((now - last) / 1000, 1 / 30) : 1 / 60;
            last = now;

            var ax = (-stiffness * (x - tx) - damping * vx) / mass;
            var ay = (-stiffness * (y - ty) - damping * vy) / mass;
            vx += ax * dt;
            vy += ay * dt;
            x += vx * dt;
            y += vy * dt;

            el.style.setProperty('--pn-mx', x.toFixed(2) + 'px');
            el.style.setProperty('--pn-my', y.toFixed(2) + 'px');

            var settled = Math.abs(x - tx) < 0.05 && Math.abs(y - ty) < 0.05 &&
                Math.abs(vx) < 0.05 && Math.abs(vy) < 0.05;

            if (settled && !hovering) {
                // hard stop: snap to rest and release the loop
                x = tx; y = ty; vx = 0; vy = 0;
                el.style.setProperty('--pn-mx', '0px');
                el.style.setProperty('--pn-my', '0px');
                raf = null; last = 0;
                return;
            }
            raf = requestAnimationFrame(step);
        }

        function start() { if (raf == null) { last = 0; raf = requestAnimationFrame(step); } }

        function onMove(e) {
            if (!rect) return;
            var cx = rect.left + rect.width / 2;
            var cy = rect.top + rect.height / 2;
            var dx = e.clientX - cx;
            var dy = e.clientY - cy;
            var dist = Math.sqrt(dx * dx + dy * dy);

            if (dist <= range) {
                var falloff = 1 - dist / range;   // the pull weakens with distance
                tx = dx * intensity * falloff;
                ty = dy * intensity * falloff;
            } else {
                tx = 0; ty = 0;
            }
            start();
        }

        el.addEventListener('pointerenter', function () {
            if (reduceMotion || e_pointerCoarse()) return;
            hovering = true;
            measure();
            window.addEventListener('pointermove', onMove, { passive: true });
        });

        el.addEventListener('pointerleave', function () {
            hovering = false;
            rect = null;
            window.removeEventListener('pointermove', onMove);
            tx = 0; ty = 0;
            start();
        });

        // A stale rect would make the pull feel wrong after any layout change.
        window.addEventListener('resize', function () { rect = null; }, { passive: true });
    }

    function e_pointerCoarse() {
        return window.matchMedia && window.matchMedia('(pointer: coarse)').matches;
    }

    /* =========================================================================
       2. CutReveal — ported vertical cut wipe
       Original: React + motion/react. Each grapheme/word sits inside an
       overflow-hidden inline-flex wrapper and travels y:100% -> 0 on a spring
       (stiffness 190-200, damping 21-22). The original wraps visible text in
       aria-hidden and exposes a single sr-only copy — kept here, because
       animating split text wrecks screen-reader output otherwise.
       ====================================================================== */
    function attachCutReveal(el) {
        var text = (el.textContent || '').trim();
        if (!text) return;

        var split = el.getAttribute('data-pn-split') || 'words';
        var stagger = parseFloat(el.getAttribute('data-pn-stagger') || '0.045') * 1000;
        var from = el.getAttribute('data-pn-from') || 'first';

        var units;
        if (split === 'chars' && window.Intl && Intl.Segmenter) {
            var seg = new Intl.Segmenter(undefined, { granularity: 'grapheme' });
            units = Array.from(seg.segment(text), function (s) { return s.segment; });
        } else if (split === 'chars') {
            units = Array.from(text);
        } else {
            units = text.split(/(\s+)/);
        }

        // Screen readers get the untouched sentence; the moving parts are hidden.
        var sr = document.createElement('span');
        sr.className = 'sr-only';
        sr.textContent = text;

        var visual = document.createElement('span');
        visual.setAttribute('aria-hidden', 'true');

        var total = units.length;
        units.forEach(function (unit, i) {
            var delay;
            if (from === 'last') delay = (total - 1 - i) * stagger;
            else if (from === 'center') delay = Math.abs(Math.floor(total / 2) - i) * stagger;
            else delay = i * stagger;

            if (/^\s+$/.test(unit)) {
                visual.appendChild(document.createTextNode(unit));
                return;
            }
            var clip = document.createElement('span');
            clip.className = 'pn-cut';
            var inner = document.createElement('span');
            inner.style.setProperty('--pn-cut-delay', delay.toFixed(0) + 'ms');
            inner.textContent = unit;
            clip.appendChild(inner);
            visual.appendChild(clip);
        });

        el.textContent = '';
        el.appendChild(sr);
        el.appendChild(visual);

        if (reduceMotion) { el.classList.add('pn-cut--static'); return; }

        observe(el, function () {
            var inners = visual.querySelectorAll('.pn-cut');
            for (var i = 0; i < inners.length; i++) inners[i].classList.add('is-in');
        }, function () {
            var inners = visual.querySelectorAll('.pn-cut');
            for (var i = 0; i < inners.length; i++) inners[i].classList.remove('is-in');
        });
    }

    /* =========================================================================
       3. Reveal — scroll entrances
       motion.csv #4/#5: 8-16px offset reads as a fade rather than a slide;
       stagger no more than 8 children or the tail feels sluggish.
       ====================================================================== */
    function attachReveal(el) {
        if (reduceMotion) return;

        var children = el.hasAttribute('data-pn-reveal-children')
            ? Array.prototype.slice.call(el.children).slice(0, 8)
            : null;

        if (children && children.length) {
            children.forEach(function (c) { c.classList.add('pn-reveal-ready'); });
        } else {
            el.classList.add('pn-reveal-ready');
        }

        observe(el, function () {
            if (children && children.length) {
                children.forEach(function (c, i) {
                    c.style.setProperty('--pn-reveal-delay', (i * 55) + 'ms');
                    c.classList.add('is-in');
                });
            } else {
                el.classList.add('is-in');
            }
        }, function () {
            if (children && children.length) {
                children.forEach(function (c) { c.classList.remove('is-in'); });
            } else {
                el.classList.remove('is-in');
            }
        });
    }

    /* A tiny shared observer, because one observer for many elements is cheaper
       than one per element. `once` behaviour maps to the reveal semantics. */
    var watching = new WeakMap();
    var sharedObserver = null;

    function getObserver() {
        if (sharedObserver) return sharedObserver;
        if (!('IntersectionObserver' in window)) return null;
        sharedObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                var rec = watching.get(entry.target);
                if (!rec) return;
                if (entry.isIntersecting) rec.onEnter(entry.target);
                else rec.onExit(entry.target);
            });
        }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
        return sharedObserver;
    }

    function observe(el, onEnter, onExit) {
        var obs = getObserver();
        if (!obs) { onEnter(el); return; }          // no IO: show the final state
        watching.set(el, { onEnter: onEnter, onExit: onExit || function () {} });
        obs.observe(el);
    }

    /* =========================================================================
       4. Ident — the brand motion graphic
       A self-contained animated SVG. No video file, so it stays crisp at any
       size, themes with the page, and costs almost nothing to load.

       Timeline (3.6s cycle):
         0.00 - 0.45  nodes light up left to right
         0.45 - 1.05  the transfer beam draws between them
         1.05 - 2.10  a packet travels from the first node to the last
         2.10 - 3.60  hold, then reset
       Only the tab being visible and the element being on screen keep it alive.
       ====================================================================== */
    function attachIdent(el) {
        var nodes = Array.prototype.slice.call(el.querySelectorAll('.pn-ident__node'));
        var beam = el.querySelector('.pn-ident__beam');
        var packet = el.querySelector('.pn-ident__packet');
        var label = el.querySelector('.pn-ident__label');
        var rings = Array.prototype.slice.call(el.querySelectorAll('.pn-ident__ring'));

        var labels = ['looking', '2 devices', 'sending', 'delivered'];
        var raf = null;
        var t0 = 0;
        var visible = true;
        var cycle = 3600;

        function easeOut(p) { return 1 - Math.pow(1 - p, 3); }

        function reset() {
            nodes.forEach(function (n) { n.classList.remove('is-on'); });
            if (beam) beam.style.transform = 'scaleX(0)';
            if (packet) packet.style.transform = 'translateX(0px)';
            rings.forEach(function (r) { r.style.transform = 'scale(.62)'; r.style.opacity = '.7'; });
            if (label) label.textContent = labels[0];
        }

        function frame(now) {
            if (!visible || document.hidden) { raf = null; return; }
            if (!t0) t0 = now;
            var t = (now - t0) % cycle;

            // rings: very slow outward drift, transform only
            var rp = easeOut(Math.min(t / 1400, 1));
            rings.forEach(function (r, i) {
                var v = Math.max(0, Math.min(1, rp - i * 0.12));
                r.style.transform = 'scale(' + (0.62 + 0.38 * v).toFixed(3) + ')';
                r.style.opacity = (0.7 - 0.45 * v).toFixed(2);
            });

            // nodes
            var nodeStart = 0, nodeStep = 150;
            nodes.forEach(function (n, i) {
                var on = t >= nodeStart + i * nodeStep;
                if (on !== n.classList.contains('is-on')) n.classList.toggle('is-on', on);
            });

            // beam
            if (beam) {
                var bp = Math.max(0, Math.min(1, (t - 450) / 600));
                beam.style.transform = 'scaleX(' + easeOut(bp).toFixed(4) + ')';
            }

            // packet travels the beam
            if (packet) {
                var pp = Math.max(0, Math.min(1, (t - 1050) / 1050));
                var dist = packet.getAttribute('data-pn-travel') || '168';
                packet.style.transform = 'translateX(' + (easeOut(pp) * parseFloat(dist)).toFixed(1) + 'px)';
            }

            // label
            if (label) {
                var li = t < 450 ? 0 : t < 1050 ? 1 : t < 2100 ? 2 : 3;
                if (label.textContent !== labels[li]) label.textContent = labels[li];
            }

            raf = requestAnimationFrame(frame);
        }

        function start() {
            if (reduceMotion) {
                // reduced motion: show the finished frame, no loop
                nodes.forEach(function (n) { n.classList.add('is-on'); });
                if (beam) beam.style.transform = 'scaleX(1)';
                if (label) label.textContent = labels[3];
                return;
            }
            if (raf == null) { t0 = 0; raf = requestAnimationFrame(frame); }
        }

        function stop() { if (raf != null) { cancelAnimationFrame(raf); raf = null; } }

        reset();

        if ('IntersectionObserver' in window) {
            new IntersectionObserver(function (entries) {
                visible = entries[0].isIntersecting;
                if (visible) start(); else stop();
            }, { threshold: 0.05 }).observe(el);
        } else {
            start();
        }

        document.addEventListener('visibilitychange', function () {
            if (document.hidden) stop();
            else if (visible) start();
        });
    }

    /* ============================================================== bootstrap */
    function init() {
        var i;

        var magnetic = document.querySelectorAll('[data-pn-magnetic]');
        for (i = 0; i < magnetic.length; i++) {
            var m = magnetic[i];
            attachMagnetic(m, {
                intensity: parseFloat(m.getAttribute('data-pn-magnetic')) || 0.6,
                range: parseFloat(m.getAttribute('data-pn-range') || '100')
            });
        }

        var cuts = document.querySelectorAll('[data-pn-cut]');
        for (i = 0; i < cuts.length; i++) attachCutReveal(cuts[i]);

        var reveals = document.querySelectorAll('[data-pn-reveal]');
        for (i = 0; i < reveals.length; i++) attachReveal(reveals[i]);

        var idents = document.querySelectorAll('.pn-ident');
        for (i = 0; i < idents.length; i++) attachIdent(idents[i]);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    window.PairNepalMotion = { init: init, attachMagnetic: attachMagnetic, attachIdent: attachIdent };
})();
