import { Capacitor } from '@capacitor/core';
import { LocalNotifications } from '@capacitor/local-notifications';
import { isPermissionGranted, requestPermission, sendNotification } from '@tauri-apps/plugin-notification';

export function useNotifications() {
  const checkPermissions = async () => {
    if (Capacitor.isNativePlatform()) {
      let permStatus = await LocalNotifications.checkPermissions();
      if (permStatus.display === 'prompt') {
        permStatus = await LocalNotifications.requestPermissions();
      }
      return permStatus.display === 'granted';
    } else {
      let permissionGranted = await isPermissionGranted();
      if (!permissionGranted) {
        const permission = await requestPermission();
        permissionGranted = permission === 'granted';
      }
      return permissionGranted;
    }
  };

  const notify = async (title: string, body: string, id: number = Math.floor(Math.random() * 100000)) => {
    const hasPermission = await checkPermissions();
    if (!hasPermission) {
      console.warn('Notification permission not granted');
      return;
    }

    if (Capacitor.isNativePlatform()) {
      await LocalNotifications.schedule({
        notifications: [
          {
            title,
            body,
            id,
            schedule: { at: new Date(Date.now() + 1000) },
            actionTypeId: '',
            extra: null,
          },
        ],
      });
    } else {
      sendNotification({ title, body });
    }
  };

  return { notify, checkPermissions };
}
