/* =============================================================================
   PairNepal — bootstrap
   -----------------------------------------------------------------------------
   Mounts the brand layer into the app without touching the app's own modules.

   Deliberately defensive: this file must never throw, because a failure here
   would take the whole file transfer UI down with it. Everything is wrapped and
   every lookup is null-checked.
   ========================================================================== */

(function () {
    'use strict';

    function mount() {
        var header = document.querySelector('body > header');
        var sound = window.PairNepalSound;
        var motion = window.PairNepalMotion;

        /* --- interface sounds -------------------------------------------------
           Placed just inside the brand lockup so it reads as a setting, not as a
           primary action. Inserted before the brand element, which is the last
           header child (the header is flex-row-reverse). */
        try {
            if (header && sound) {
                var btn = sound.button();
                var brand = header.querySelector('.pn-brand');
                if (brand) header.insertBefore(btn, brand);
                else header.appendChild(btn);

                sound.bindToApp();
            }
        } catch (e) {
            console.warn('[PairNepal] sound layer unavailable:', e);
        }

        /* --- motion + ident --------------------------------------------------- */
        try {
            if (motion && motion.init) motion.init();
        } catch (e) {
            console.warn('[PairNepal] motion layer unavailable:', e);
        }

        /* --- signalling notice ------------------------------------------------ */
        try { watchSignaling(); } catch (e) {
            console.warn('[PairNepal] signal watcher unavailable:', e);
        }

        /* --- keyboard escape hatch -------------------------------------------
           A hidden-first skip link so keyboard users can jump past the header. */
        try {
            if (document.body && !document.querySelector('.pn-skip')) {
                var skip = document.createElement('a');
                skip.className = 'pn-skip';
                skip.href = '#center';
                skip.textContent = 'Skip to devices';
                document.body.insertBefore(skip, document.body.firstChild);
            }
        } catch (e) { /* non-essential */ }
    }

    /* ---------------------------------------------------------------------
       Signalling notice.

       Discovery needs a long-lived WebSocket to the signalling server. On a
       host that cannot keep sockets open the connection simply keeps failing,
       and the app would otherwise look broken with no explanation. The notice
       appears only after three consecutive failures, so a correctly configured
       instance never shows it.
       ------------------------------------------------------------------ */
    function watchSignaling() {
        var failures = 0;
        var shown = false;

        function onFailure() {
            failures++;
            if (shown || failures < 3) return;
            shown = true;
            showNotice();
        }

        // `Events` is declared by the app's own scripts, so it may not exist yet.
        if (typeof Events === 'undefined' || !Events.on) return;
        Events.on('pn-signal-error', onFailure);
    }

    function showNotice() {
        if (document.querySelector('.pn-notice')) return;

        var el = document.createElement('div');
        el.className = 'pn-notice';
        el.setAttribute('role', 'status');
        el.innerHTML =
            '<div class="pn-notice__body">' +
            '<strong>Device discovery is unavailable</strong>' +
            'This instance cannot reach its signalling service, so devices cannot find each other. ' +
            'Transfers need it. If you run this site, attach a signalling server to enable them.' +
            '</div>' +
            '<button class="pn-notice__close" type="button" aria-label="Dismiss">&times;</button>';

        el.querySelector('.pn-notice__close').addEventListener('click', function () {
            el.remove();
        });

        document.body.appendChild(el);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', mount);
    } else {
        mount();
    }
})();
