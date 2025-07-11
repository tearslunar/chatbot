// Service Worker for Hi-Care AI 챗봇
const CACHE_NAME = 'hi-care-chatbot-v2.0';
const STATIC_CACHE = 'static-cache-v2.0';
const DYNAMIC_CACHE = 'dynamic-cache-v2.0';

// 필수 리소스 (오프라인에서도 접근 가능해야 함)
const ESSENTIAL_RESOURCES = [
  '/',
  '/index.html',
  '/offline.html'
];

// 캐시할 정적 리소스 패턴
const STATIC_PATTERNS = [
  /\.css$/,
  /\.js$/,
  /\.woff2?$/,
  /\.png$/,
  /\.jpg$/,
  /\.jpeg$/,
  /\.svg$/,
  /\.ico$/
];

// 캐시하지 않을 리소스
const EXCLUDE_PATTERNS = [
  /\/api\//,
  /analytics/,
  /gtag/,
  /hot-update/
];

self.addEventListener('install', event => {
  console.log('[SW] 설치 중...');
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('[SW] 필수 리소스 캐싱 중...');
        return cache.addAll(ESSENTIAL_RESOURCES);
      })
      .then(() => {
        console.log('[SW] 설치 완료');
        return self.skipWaiting();
      })
      .catch(error => {
        console.error('[SW] 설치 실패:', error);
      })
  );
});

self.addEventListener('activate', event => {
  console.log('[SW] 활성화 중...');
  event.waitUntil(
    Promise.all([
      // 오래된 캐시 정리
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log('[SW] 오래된 캐시 삭제:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      // 클라이언트 즉시 제어
      self.clients.claim()
    ]).then(() => {
      console.log('[SW] 활성화 완료');
    })
  );
});

self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // EXCLUDE_PATTERNS에 해당하는 요청은 캐시하지 않음
  if (EXCLUDE_PATTERNS.some(pattern => pattern.test(request.url))) {
    return fetch(request);
  }

  // GET 요청만 캐시 처리
  if (request.method !== 'GET') {
    return fetch(request);
  }

  event.respondWith(
    caches.match(request)
      .then(cachedResponse => {
        if (cachedResponse) {
          // 캐시된 리소스가 있으면 바로 반환
          console.log('[SW] 캐시에서 반환:', request.url);
          
          // 백그라운드에서 업데이트 확인 (stale-while-revalidate)
          if (shouldUpdateInBackground(request)) {
            fetch(request)
              .then(networkResponse => {
                if (networkResponse && networkResponse.status === 200) {
                  const responseClone = networkResponse.clone();
                  const cacheName = getCacheName(request);
                  caches.open(cacheName).then(cache => {
                    cache.put(request, responseClone);
                  });
                }
              })
              .catch(() => {
                // 네트워크 실패는 무시 (캐시된 버전 사용)
              });
          }
          
          return cachedResponse;
        }
        
        // 캐시에 없으면 네트워크에서 가져오기
        return fetch(request)
          .then(networkResponse => {
            // 응답이 유효한지 확인
            if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
              return networkResponse;
            }
            
            // 캐시할지 결정
            if (shouldCache(request)) {
              const responseClone = networkResponse.clone();
              const cacheName = getCacheName(request);
              
              caches.open(cacheName).then(cache => {
                console.log('[SW] 새 리소스 캐싱:', request.url);
                cache.put(request, responseClone);
              });
            }
            
            return networkResponse;
          })
          .catch(() => {
            // 네트워크 실패 시 오프라인 페이지 반환
            if (request.destination === 'document') {
              return caches.match('/offline.html');
            }
            
            // 다른 리소스는 빈 응답 반환
            return new Response('', { status: 408, statusText: 'Offline' });
          });
      })
  );
});

// 캐시 이름 결정
function getCacheName(request) {
  return isStaticResource(request) ? STATIC_CACHE : DYNAMIC_CACHE;
}

// 정적 리소스인지 판단
function isStaticResource(request) {
  return STATIC_PATTERNS.some(pattern => pattern.test(request.url));
}

// 캐시해야 하는지 판단
function shouldCache(request) {
  const url = new URL(request.url);
  
  // 같은 오리진이거나 정적 리소스만 캐시
  return url.origin === self.location.origin || isStaticResource(request);
}

// 백그라운드 업데이트가 필요한지 판단
function shouldUpdateInBackground(request) {
  // HTML, CSS, JS 파일은 백그라운드 업데이트
  return /\.(html|css|js)$/.test(request.url);
}

// 메시지 처리
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// 백그라운드 동기화 (선택사항)
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    console.log('[SW] 백그라운드 동기화 실행');
    // 필요시 백그라운드 동기화 로직 추가
  }
});

// 푸시 알림 처리 (선택사항)
self.addEventListener('push', event => {
  if (event.data) {
    const options = {
      body: event.data.text(),
      icon: '/icon-192x192.png',
      badge: '/icon-72x72.png',
      vibrate: [100, 50, 100],
      data: {
        dateOfArrival: Date.now(),
        primaryKey: 1
      }
    };
    
    event.waitUntil(
      self.registration.showNotification('Hi-Care 챗봇', options)
    );
  }
});

console.log('[SW] Service Worker 등록됨'); 