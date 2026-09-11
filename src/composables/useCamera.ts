import { Capacitor } from '@capacitor/core';
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';

export function useCamera() {
  const takePhoto = async (): Promise<string | null> => {
    if (!Capacitor.isNativePlatform()) {
      console.warn('Camera is only supported on native platforms. Using fallback input on web.');
      // Fallback to file input is handled in UI components usually
      return null;
    }

    try {
      const image = await Camera.getPhoto({
        quality: 90,
        allowEditing: false,
        resultType: CameraResultType.Uri,
        source: CameraSource.Prompt // Prompts user to choose photo or take a new one
      });

      return image.webPath || null;
    } catch (e) {
      console.error('Failed to take photo', e);
      return null;
    }
  };

  return { takePhoto };
}
