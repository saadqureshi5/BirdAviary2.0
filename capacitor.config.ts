import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.birdaviary2.app',
  appName: 'BirdAviary2.0',
  webDir: 'dist',
  plugins: {
    CapacitorSQLite: {
      iosDatabaseLocation: 'Library/CapacitorDatabase',
      iosIsEncryption: false,
      iosKeychainPrefix: 'birdaviary',
      iosBiometric: {
        biometricAuth: false,
        biometricTitle: "Biometric login for capacitor sqlite"
      },
      androidIsEncryption: false,
      androidBiometric: {
        biometricAuth: false,
        biometricTitle: "Biometric login for capacitor sqlite",
        biometricSubTitle: "Log in using your biometric"
      },
    },
    GoogleAuth: {
      scopes: ['profile', 'email', 'https://www.googleapis.com/auth/drive.appdata'],
      serverClientId: '923599076322-d4mo1qchirsu7bvu525pqur9fr3nld3d.apps.googleusercontent.com',
      forceCodeForRefreshToken: true,
      iosClientId: '923599076322-emosrtvl2tsdm7dirvk0fo7lhlvp7qnt.apps.googleusercontent.com',
      androidClientId: '923599076322-dqe5m6snv7jmrckdlq1ei25fek6qmtei.apps.googleusercontent.com'
    }
  }
};

export default config;
