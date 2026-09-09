import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useStore } from '../store/useStore';
import { RootStackParamList } from './types';
import { PanicToggle } from '../components/PanicToggle';
import { theme } from '../theme/theme';

import { AuthScreen } from '../screens/AuthScreen';
import { BranchSelectScreen } from '../screens/BranchSelectScreen';
import { HomeScreen } from '../screens/HomeScreen';
import { SubjectScreen } from '../screens/SubjectScreen';
import { TopicListScreen } from '../screens/TopicListScreen';
import { SwipeScreen } from '../screens/SwipeScreen';
import { ContentScreen } from '../screens/ContentScreen';

const Stack = createNativeStackNavigator<RootStackParamList>();

export const RootNavigator = () => {
  const token = useStore((state) => state.token);

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerStyle: { backgroundColor: theme.colors.surface },
          headerTintColor: theme.colors.text,
          headerRight: () => token ? <PanicToggle /> : null,
        }}
      >
        {!token ? (
          <Stack.Screen name="Auth" component={AuthScreen} options={{ headerShown: false }} />
        ) : (
          <>
            <Stack.Screen name="BranchSelect" component={BranchSelectScreen} options={{ title: 'Select Branch' }} />
            <Stack.Screen name="Home" component={HomeScreen} options={{ title: 'Select Semester' }} />
            <Stack.Screen name="Subject" component={SubjectScreen} options={{ title: 'Select Subject' }} />
            <Stack.Screen name="TopicList" component={TopicListScreen} options={{ title: 'Topics' }} />
            <Stack.Screen name="Swipe" component={SwipeScreen} options={{ title: 'LearnSwipe' }} />
            <Stack.Screen name="Content" component={ContentScreen} options={{ title: 'Topic Content' }} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};
