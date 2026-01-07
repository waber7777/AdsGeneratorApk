import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'ru.logicgames.sudokumaster',
  appName: 'Судоку Мастер',
  webDir: 'dist',
  android: {
    backgroundColor: '#0a0a0f'
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#0a0a0f',
      showSpinner: false
    }
  }
};

export default config;




