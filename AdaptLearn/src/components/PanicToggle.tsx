import React, { useEffect, useState } from 'react';
import { Animated, Pressable, StyleSheet, Text, View } from 'react-native';
import { useAppStore } from '../store/useStore';
import { theme } from '../theme/theme';
import PanicModal from './PanicModal';
import { endPanicSession } from '../api/panic';

function useCountdownLabel(deadline?: string) {
  const [label, setLabel] = useState('--');

  useEffect(() => {
    if (!deadline) {
      setLabel('--');
      return;
    }
    const update = () => {
      const diffMs = new Date(deadline).getTime() - Date.now();
      if (diffMs <= 0) {
        setLabel('Time up');
        return;
      }
      const totalHours = Math.floor(diffMs / (1000 * 60 * 60));
      const minutes = Math.floor((diffMs / (1000 * 60)) % 60);
      if (totalHours >= 24) {
        setLabel(`${Math.floor(totalHours / 24)}d ${totalHours % 24}h left`);
      } else {
        setLabel(`${totalHours}h ${minutes}m left`);
      }
    };
    update();
    const interval = setInterval(update, 60 * 1000);
    return () => clearInterval(interval);
  }, [deadline]);

  return label;
}

export default function PanicToggle() {
  const panicSession = useAppStore((s) => s.panicSession);
  const setPanicSession = useAppStore((s) => s.setPanicSession);
  const [modalVisible, setModalVisible] = useState(false);
  const pulse = React.useRef(new Animated.Value(1)).current;
  const countdownLabel = useCountdownLabel(panicSession?.deadline);

  useEffect(() => {
    if (!panicSession) return;
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(pulse, { toValue: 1.15, duration: 700, useNativeDriver: true }),
        Animated.timing(pulse, { toValue: 1, duration: 700, useNativeDriver: true }),
      ])
    );
    loop.start();
    return () => loop.stop();
  }, [panicSession, pulse]);

  async function handlePress() {
    if (panicSession) {
      // Tapping an active toggle ends Panic Mode. Best-effort on the
      // network call — a failed DELETE shouldn't trap the student in a
      // stale urgency state, so we clear local state regardless.
      endPanicSession(panicSession.id).catch(() => {});
      setPanicSession(null);
      return;
    }
    setModalVisible(true);
  }

  return (
    <View style={styles.wrapper}>
      <Pressable
        onPress={handlePress}
        style={[styles.pill, panicSession ? styles.pillActive : styles.pillIdle]}
        accessibilityRole="switch"
        accessibilityState={{ checked: !!panicSession }}
        accessibilityLabel="Panic toggle — set exam countdown"
      >
        <Animated.View
          style={[
            styles.dot,
            { backgroundColor: panicSession ? theme.color.panic : theme.color.textMuted },
            panicSession ? { transform: [{ scale: pulse }] } : null,
          ]}
        />
        <Text style={styles.label}>
          {panicSession ? `Panic Mode · ${countdownLabel}` : 'Panic Toggle'}
        </Text>
      </Pressable>

      <PanicModal visible={modalVisible} onClose={() => setModalVisible(false)} />
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    paddingHorizontal: theme.spacing(4),
    paddingTop: theme.spacing(2),
    paddingBottom: theme.spacing(1),
    backgroundColor: theme.color.background,
  },
  pill: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    paddingVertical: theme.spacing(2),
    paddingHorizontal: theme.spacing(3),
    borderRadius: theme.radius.pill,
    borderWidth: 1,
  },
  pillIdle: {
    backgroundColor: theme.color.surface,
    borderColor: theme.color.border,
  },
  pillActive: {
    backgroundColor: theme.color.panicMuted,
    borderColor: theme.color.panic,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: theme.spacing(2),
  },
  label: {
    color: theme.color.textPrimary,
    fontWeight: '600',
    fontSize: 13,
  },
});
