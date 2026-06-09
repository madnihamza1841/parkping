importScripts('https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.12.2/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: 'AIzaSyAg5PwASiFCxDf9IgFsR1c3VgAZ2H1p9vw',
  authDomain: 'parkping-3ab10.firebaseapp.com',
  projectId: 'parkping-3ab10',
  storageBucket: 'parkping-3ab10.firebasestorage.app',
  messagingSenderId: '204150422818',
  appId: '1:204150422818:web:c7369d69d323aecd32f97b',
});

const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
  const { title, body } = payload.notification ?? {};
  const data = payload.data ?? {};

  self.registration.showNotification(title || 'ParkPing', {
    body: body || '',
    icon: '/favicon.svg',
    data,
  });
});

// On notification click — open the relevant chat thread or call screen
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const data = event.notification.data ?? {};
  let url = '/chat';
  if (data.thread_id) url = `/chat/${data.thread_id}`;
  event.waitUntil(clients.openWindow(url));
});
