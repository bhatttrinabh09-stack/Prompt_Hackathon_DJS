import React from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';
import { theme } from '../theme/theme';

interface Props {
  title: string;
  isLocked?: boolean;
  onPress?: () => void;
}

export const GridTile: React.FC<Props> = ({ title, isLocked, onPress }) => {
  return (
    <TouchableOpacity 
      style={[styles.tile, isLocked && styles.tileLocked]} 
      onPress={isLocked ? undefined : onPress}
      disabled={isLocked}
    >
      <Text style={[styles.title, isLocked && styles.titleLocked]}>
        {title}
      </Text>
      {isLocked && <Text style={styles.lockedText}>Locked</Text>}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  tile: {
    backgroundColor: theme.colors.surface,
    padding: theme.spacing.xl,
    borderRadius: theme.borderRadius.lg,
    margin: theme.spacing.sm,
    flex: 1,
    minHeight: 120,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: theme.colors.primary,
  },
  tileLocked: {
    borderColor: 'transparent',
    opacity: 0.5,
  },
  title: {
    color: theme.colors.text,
    fontSize: theme.typography.h3.fontSize,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  titleLocked: {
    color: theme.colors.textSecondary,
  },
  lockedText: {
    color: theme.colors.textSecondary,
    fontSize: theme.typography.caption.fontSize,
    marginTop: theme.spacing.sm,
  },
});
