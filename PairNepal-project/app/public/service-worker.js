const cacheVersion = 'v1.11.2-8e73e9cb27';
const cacheTitle = `pairnepal-cache-${cacheVersion}`;
// The marketing pages are served through extensionless URLs
// (/how-it-works, /faq) and are not needed for offline app use, so they
// are deliberately not precached.
const relativePathsToCache = [
    './',
    'manifest.json',
    'styles/styles-main.css',
    'styles/styles-deferred.css',
    'styles/brand.css',
    'styles/landing.css',
    'scripts/browser-tabs-connector.js',
    'scripts/localization.js',
    'scripts/main.js',
    'scripts/network.js',
    'scripts/persistent-storage.js',
    'scripts/ui.js',
    'scripts/ui-main.js',
    'scripts/util.js',
    'scripts/pairnepal-sound.js',
    'scripts/pairnepal-motion.js',
    'scripts/pairnepal-boot.js',
    'scripts/worker/canvas-worker.js',
    'scripts/libs/heic2any.min.js',
    'scripts/libs/no-sleep.min.js',
    'scripts/libs/qr-code.min.js',
    'scripts/libs/zip.min.js',
    'sounds/blop.mp3',
    'sounds/blop.ogg',
    'images/favicon-96x96.png',
    'images/favicon-96x96-notification.png',
    'images/android-chrome-192x192.png',
    'images/android-chrome-192x192-maskable.png',
    'images/android-chrome-512x512.png',
    'images/android-chrome-512x512-maskable.png',
    'images/apple-touch-icon.png',
    'fonts/OpenSans/static/OpenSans-Medium.ttf',
    'lang/ar.json',
    'lang/be.json',
    'lang/bg.json',
    'lang/ca.json',
    'lang/cs.json',
    'lang/da.json',
    'lang/de.json',
    'lang/en.json',
    'lang/es.json',
    'lang/et.json',
    'lang/eu.json',
    'lang/fa.json',
    'lang/fr.json',
    'lang/he.json',
    'lang/hu.json',
    'lang/id.json',
    'lang/it.json',
    'lang/ja.json',
    'lang/kn.json',
    'lang/ko.json',
    'lang/nb.json',
    'lang/nl.json',
    'lang/nn.json',
    'lang/pl.json',
    'lang/pt-BR.json',
    'lang/ro.json',
    'lang/ru.json',
    'lang/sk.json',
    'lang/ta.json',
    'lang/tr.json',
    'lang/uk.json',
    'lang/zh-CN.json',
    'lang/zh-HK.json',
    'lang/zh-TW.json'
];
const relativePathsNotToCache = [
    'config'
]

self.addEventListener('install', function(event) {
    // Perform install steps
    console.log("Cache files for sw:", cacheVersion);
    event.waitUntil(
        caches.open(cacheTitle)
            .then(function(cache) {
                return cache
                    .addAll(relativePathsToCache)
                    .then(_ => {
                        console.log('All files cached for sw:', cacheVersion);
                        self.skipWaiting();
                    });
            })
    );
});

// fetch the resource from the network
const fromNetwork = (request, timeout) =>
    new Promise((resolve, reject) => {
        const timeoutId = setTimeout(reject, timeout);
        fetch(request, {cache: "no-store"})
            .then(response => {
                clearTimeout(timeoutId);
                resolve(response);

                // A redirected response must never be cached under the original
                // request key (the legacy .html URLs 301 to the canonical ones),
                // but it must still be handed back so the browser can follow it.
                if (response.redirected) return;

                // Prevent requests that are in relativePathsNotToCache from being cached
                if (doNotCacheRequest(request)) return;

                updateCache(request)
                    .then(() => console.log("Cache successfully updated for", request.url))
                    .catch(err => console.log("Cache could not be updated for", request.url, err));
            })
            .catch(error => {
                // Handle any errors that occurred during the fetch
                console.error(`Could not fetch ${request.url}.`);
                reject(error);
            });
    });

// fetch the resource from the browser cache
const fromCache = request =>
    caches
        .open(cacheTitle)
        .then(cache =>
            cache.match(request)
        );

const rootUrl = location.href.substring(0, location.href.length - "service-worker.js".length);
const rootUrlLength = rootUrl.length;

const doNotCacheRequest = request => {
    const requestRelativePath = request.url.substring(rootUrlLength);
    return relativePathsNotToCache.indexOf(requestRelativePath) !== -1
};

// cache the current page to make it available for offline
const updateCache = request => new Promise((resolve, reject) => {
    caches
        .open(cacheTitle)
        .then(cache =>
            fetch(request, {cache: "no-store"})
                .then(response => {
                    // Nothing to store for a redirect; resolve so the caller is
                    // not left hanging on a promise that never settles.
                    if (response.redirected) {
                        resolve();
                        return;
                    }

                    cache
                        .put(request, response)
                        .then(() => resolve());
                })
                .catch(reason => reject(reason))
        );
});

// general strategy when making a request:
// 1. Try to retrieve file from cache
// 2. If cache is not available: Fetch from network and update cache.
// This way, cached files are only updated if the cacheVersion is changed
self.addEventListener('fetch', function(event) {
    const swOrigin = new URL(self.location.href).origin;
    const requestOrigin = new URL(event.request.url).origin;

    if (swOrigin !== requestOrigin) {
        // Do not handle requests from other origin
        event.respondWith(fetch(event.request));
    }
    else if (event.request.method === "POST") {
        // Requests related to Web Share Target.
        event.respondWith((async () => {
            const share_url = await evaluateRequestData(event.request);
            return Response.redirect(encodeURI(share_url), 302);
        })());
    }
    else {
        // Regular requests not related to Web Share Target:
        // If request is excluded from cache -> respondWith fromNetwork
        // else -> try fromCache first
        event.respondWith(
            doNotCacheRequest(event.request)
                ? fromNetwork(event.request, 10000)
                // Network-first: serve the live file and refresh the cache in the
                // background, falling back to the cached copy only when offline.
                // Cache-first (upstream's default) meant a returning visitor kept
                // seeing the stylesheet they downloaded on their first visit.
                : fromNetwork(event.request, 5000)
                    .catch(() => fromCache(event.request))
                    .then(response => response || fromCache(event.request))
                    .then(rsp => {
                        // if fromCache resolves to undefined fetch from network instead
                        if (!rsp) {
                            throw new Error("No match found.");
                        }
                        return rsp;
                    })
                    .catch(error => {
                        console.error("Could not retrieve request from cache:", event.request.url, error);
                        return fromNetwork(event.request, 10000);
                    })
        );
    }
});


// on activation, we clean up the previously registered service workers
self.addEventListener('activate', evt => {
    console.log("Activate sw:", cacheVersion);
    evt.waitUntil(clients.claim());
    return evt.waitUntil(
        caches
            .keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== cacheTitle) {
                            console.log("Delete cache:", cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
    )
});

const evaluateRequestData = function (request) {
    return new Promise(async (resolve) => {
        const formData = await request.formData();
        const title = formData.get("title");
        const text = formData.get("text");
        const url = formData.get("url");
        const files = formData.getAll("allfiles");

        const pairDropUrl = request.url;

        if (files && files.length > 0) {
            let fileObjects = [];
            for (let i=0; i<files.length; i++) {
                fileObjects.push({
                    name: files[i].name,
                    buffer: await files[i].arrayBuffer()
                });
            }

            const DBOpenRequest = indexedDB.open('pairdrop_store');
            DBOpenRequest.onsuccess = e => {
                const db = e.target.result;
                for (let i = 0; i < fileObjects.length; i++) {
                    const transaction = db.transaction('share_target_files', 'readwrite');
                    const objectStore = transaction.objectStore('share_target_files');

                    const objectStoreRequest = objectStore.add(fileObjects[i]);
                    objectStoreRequest.onsuccess = _ => {
                        if (i === fileObjects.length - 1) resolve(pairDropUrl + '?share_target=files');
                    }
                }
            }
            DBOpenRequest.onerror = _ => {
                resolve(pairDropUrl);
            }
        }
        else {
            let urlArgument = '?share_target=text';

            if (title) urlArgument += `&title=${title}`;
            if (text) urlArgument += `&text=${text}`;
            if (url) urlArgument += `&url=${url}`;

            resolve(pairDropUrl + urlArgument);
        }
    });
}
