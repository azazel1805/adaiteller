// This script registers the service worker.

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    // Use the correct path relative to the root domain
    navigator.serviceWorker.register('/static/sw.js') // Path to YOUR service worker file
      .then(registration => {
        console.log('ServiceWorker registration successful with scope: ', registration.scope);

        // Optional: Track updates to the service worker
        registration.onupdatefound = () => {
          const installingWorker = registration.installing;
          if (installingWorker == null) {
            return;
          }
          installingWorker.onstatechange = () => {
            if (installingWorker.state === 'installed') {
              if (navigator.serviceWorker.controller) {
                // New content is available and will be used when all tabs for this scope are closed.
                console.log('New content is available; please refresh.');
                // Optional: Show a toast or notification to the user prompting them to refresh.
                // showRefreshUI(registration);
              } else {
                // Content is cached for offline use.
                console.log('Content is cached for offline use.');
              }
            }
          };
        };

      })
      .catch(error => {
        console.log('ServiceWorker registration failed: ', error);
      });
  });

   // Optional: Listen for controller change - occurs when a new SW takes over. Refresh page?
   navigator.serviceWorker.oncontrollerchange = () => {
     console.log('Controller changed. Page will reload.');
     window.location.reload(); // Force reload to use the new service worker immediately
   };

} else {
    console.log('Service workers are not supported in this browser.');
}

// Optional: UI function to prompt user to refresh (example)
function showRefreshUI(registration) {
  // Create a button or notification element
  const refreshButton = document.createElement('button');
  refreshButton.style.position = 'fixed';
  refreshButton.style.bottom = '20px';
  refreshButton.style.left = '20px';
  refreshButton.style.zIndex = '1000';
  refreshButton.textContent = 'New version available. Refresh?';
  refreshButton.addEventListener('click', () => {
    if (!registration.waiting) {
      // Just reload the page if there is no waiting worker - something went wrong?
      window.location.reload();
      return;
    }
    // Tell the waiting worker to activate
    refreshButton.disabled = true;
    registration.waiting.postMessage({ type: 'SKIP_WAITING' });
  });
  document.body.appendChild(refreshButton);
}
