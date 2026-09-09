import 'react-native-gesture-handler';
import React, { useEffect, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import RootNavigator from './src/navigation/RootNavigator';
import LoadingView from './src/components/LoadingView';
import { theme } from './src/theme/theme';
import { useAppStore, hydrateSessionFromSecureStore } from './src/store/useStore';
import { getCurrentUser } from './src/api/auth';
import { View, StyleSheet } from 'react-native';

export default function App() {
  const [hydrating, setHydrating] = useState(true);
  const setUser = useAppStore((s) => s.setUser);
  const clearSession = useAppStore((s) => s.clearSession);

  useEffect(() => {
    (async () => {
      const token = await hydrateSessionFromSecureStore();
      if (token) {
        try {
          const user = await getCurrentUser();
          setUser(user);
        } catch {
          // Persisted token is no longer valid — fall back to the auth
          // screen rather than getting stuck on a broken session.
          await clearSession();
        }
      }
      setHydrating(false);
    })();
  }, [setUser, clearSession]);

  if (hydrating) {
    return (
      <View style={styles.splash}>
        <LoadingView label="Getting things ready…" />
      </View>
    );
  }

  return (
    <>
      <StatusBar style="light" />
      <RootNavigator />
    </>
  );
}

const styles = StyleSheet.create({
  splash: { flex: 1, backgroundColor: theme.color.background },
});
