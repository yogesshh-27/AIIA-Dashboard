/**
 * IndexedDB Offline Storage & Synchronization Engine
 * Enables field investigators in rural Ayush clinics to record patient & adverse event data offline.
 */

const DB_NAME = 'AyurCtmsOfflineDB';
const DB_VERSION = 1;
const STORES = ['offline_adverse_events', 'offline_patient_matches', 'offline_approvals'];

function openDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      STORES.forEach((store) => {
        if (!db.objectStoreNames.contains(store)) {
          db.createObjectStore(store, { keyPath: 'id', autoIncrement: true });
        }
      });
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

export const offlineStorage = {
  async saveOffline(storeName, data) {
    try {
      const db = await openDatabase();
      return new Promise((resolve, reject) => {
        const tx = db.transaction(storeName, 'readwrite');
        const store = tx.objectStore(storeName);
        const record = {
          ...data,
          queuedAt: new Date().toISOString(),
          synced: false,
        };
        const req = store.add(record);
        req.onsuccess = () => resolve({ success: true, id: req.result });
        req.onerror = () => reject(req.error);
      });
    } catch (e) {
      console.warn('IndexedDB unavailable, falling back to localStorage');
      const list = JSON.parse(localStorage.getItem(`ayur_${storeName}`) || '[]');
      list.push({ ...data, queuedAt: new Date().toISOString() });
      localStorage.setItem(`ayur_${storeName}`, JSON.stringify(list));
      return { success: true };
    }
  },

  async getPendingCount() {
    try {
      const db = await openDatabase();
      let total = 0;
      for (const storeName of STORES) {
        total += await new Promise((resolve) => {
          const tx = db.transaction(storeName, 'readonly');
          const store = tx.objectStore(storeName);
          const countReq = store.count();
          countReq.onsuccess = () => resolve(countReq.result);
          countReq.onerror = () => resolve(0);
        });
      }
      return total;
    } catch (e) {
      return 0;
    }
  },

  async syncAllPending(apiClient) {
    if (!navigator.onLine) return { synced: 0 };
    let synced = 0;
    try {
      const db = await openDatabase();
      for (const storeName of STORES) {
        const items = await new Promise((resolve) => {
          const tx = db.transaction(storeName, 'readonly');
          const store = tx.objectStore(storeName);
          const req = store.getAll();
          req.onsuccess = () => resolve(req.result);
          req.onerror = () => resolve([]);
        });

        for (const item of items) {
          try {
            if (storeName === 'offline_adverse_events' && apiClient?.reportAdverseEvent) {
              await apiClient.reportAdverseEvent(item);
            }
            // Remove after sync
            const delTx = db.transaction(storeName, 'readwrite');
            delTx.objectStore(storeName).delete(item.id);
            synced++;
          } catch (err) {
            console.warn('Sync failed for item', item.id, err);
          }
        }
      }
    } catch (e) {
      console.error('Offline sync error', e);
    }
    return { synced };
  }
};
