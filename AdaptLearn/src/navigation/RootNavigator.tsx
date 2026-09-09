import React from 'react';
import { NavigationContainer, DefaultTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAppStore } from '../store/useStore';
import { theme } from '../theme/theme';
import { RootStackParamList } from './types';

import AuthScreen from '../screens/AuthScreen';
import BranchSelectScreen from '../screens/BranchSelectScreen';
import HomeScreen from '../screens/HomeScreen';
import SemesterScreen from '../screens/SemesterScreen';
import SubjectScreen from '../screens/SubjectScreen';
import TopicListScreen from '../screens/TopicListScreen';
import SwipeScreen from '../screens/SwipeScreen';
import ContentScreen from '../screens/ContentScreen';

const Stack = createNativeStackNavigator<RootStackParamList>();

const navTheme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    background: theme.color.background,
    card: theme.color.surface,
    text: theme.color.textPrimary,
    border: theme.color.border,
    primary: theme.color.accent,
  },
};

// Three-tier gating: no token -> Auth, token but no branch -> BranchSelect,
// otherwise the full app. This keeps onboarding order enforced (login,
// then branch) without extra guard logic scattered across screens.
export default function RootNavigator() {
  const authToken = useAppStore((s) => s.authToken);
  const user = useAppStore((s) => s.user);

  return (
    <NavigationContainer theme={navTheme}>
      <Stack.Navigator
        screenOptions={{
          headerStyle: { backgroundColor: theme.color.surface },
          headerTintColor: theme.color.textPrimary,
          headerShadowVisible: false,
        }}
      >
        {!authToken ? (
          <Stack.Screen name="Auth" component={AuthScreen} options={{ headerShown: false }} />
        ) : !user?.branch ? (
          <Stack.Screen
            name="BranchSelect"
            component={BranchSelectScreen}
            options={{ title: 'Choose Branch' }}
          />
        ) : (
          <>
            <Stack.Screen name="Home" component={HomeScreen} options={{ headerShown: false }} />
            <Stack.Screen name="Semester" component={SemesterScreen} options={{ title: 'Choose Semester' }} />
            <Stack.Screen name="Subject" component={SubjectScreen} options={{ title: 'Choose Subject' }} />
            <Stack.Screen
              name="TopicList"
              component={TopicListScreen}
              options={({ route }) => ({ title: route.params.subjectName })}
            />
            <Stack.Screen
              name="Swipe"
              component={SwipeScreen}
              options={({ route }) => ({ title: route.params.topicTitle })}
            />
            <Stack.Screen name="Content" component={ContentScreen} options={{ headerShown: false }} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
