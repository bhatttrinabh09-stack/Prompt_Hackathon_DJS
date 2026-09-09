import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Modal, TextInput, Alert } from 'react-native';
import { theme } from '../theme/theme';
import { useStore } from '../store/useStore';
import { panicApi } from '../api/client';
import { differenceInHours, parseISO } from 'date-fns';

export const PanicToggle: React.FC = () => {
  const { activeSession, setPanicSession, setUrgency, urgency } = useStore();
  const [modalVisible, setModalVisible] = useState(false);
  const [hoursInput, setHoursInput] = useState('24');
  const [timeLeft, setTimeLeft] = useState('');

  useEffect(() => {
    if (!activeSession) return;
    
    const interval = setInterval(() => {
      const now = new Date();
      const examDate = parseISO(activeSession.exam_date + 'Z'); // Handle UTC properly depending on backend
      const hours = differenceInHours(examDate, now);
      setTimeLeft(hours > 0 ? `${hours}h remaining` : 'Exam time!');
    }, 1000);
    return () => clearInterval(interval);
  }, [activeSession]);

  const handleActivate = async () => {
    try {
      const targetHours = parseInt(hoursInput, 10);
      if (isNaN(targetHours) || targetHours <= 0) {
        Alert.alert('Invalid', 'Please enter valid hours');
        return;
      }
      const session = await panicApi.setPanicSession(targetHours);
      setPanicSession(session);
      setUrgency(session.urgency_tier);
      setModalVisible(false);
    } catch (error) {
      console.error(error);
      Alert.alert('Error', 'Could not activate panic mode');
    }
  };

  const getUrgencyColor = () => {
    switch (urgency) {
      case 'high': return theme.colors.urgency.high;
      case 'medium': return theme.colors.urgency.medium;
      case 'low': return theme.colors.urgency.low;
      default: return theme.colors.urgency.low;
    }
  };

  return (
    <>
      <TouchableOpacity 
        style={[styles.container, { borderColor: getUrgencyColor() }]} 
        onPress={() => setModalVisible(true)}
      >
        <Text style={[styles.text, { color: getUrgencyColor() }]}>
          {activeSession ? timeLeft : 'Panic Mode'}
        </Text>
      </TouchableOpacity>

      <Modal visible={modalVisible} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Set Exam Deadline</Text>
            <Text style={styles.modalLabel}>Hours until exam:</Text>
            <TextInput
              style={styles.input}
              keyboardType="number-pad"
              value={hoursInput}
              onChangeText={setHoursInput}
            />
            <View style={styles.buttonRow}>
              <TouchableOpacity style={styles.cancelButton} onPress={() => setModalVisible(false)}>
                <Text style={styles.cancelText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.activateButton} onPress={handleActivate}>
                <Text style={styles.activateText}>Activate</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    borderWidth: 2,
    borderRadius: theme.borderRadius.full,
    marginRight: theme.spacing.md,
  },
  text: {
    fontWeight: 'bold',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: theme.colors.surface,
    padding: theme.spacing.xl,
    borderRadius: theme.borderRadius.lg,
    width: '80%',
  },
  modalTitle: {
    color: theme.colors.text,
    fontSize: theme.typography.h2.fontSize,
    fontWeight: 'bold',
    marginBottom: theme.spacing.md,
  },
  modalLabel: {
    color: theme.colors.textSecondary,
    marginBottom: theme.spacing.sm,
  },
  input: {
    backgroundColor: theme.colors.background,
    color: theme.colors.text,
    padding: theme.spacing.md,
    borderRadius: theme.borderRadius.md,
    marginBottom: theme.spacing.lg,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: theme.spacing.md,
  },
  cancelButton: {
    padding: theme.spacing.sm,
  },
  cancelText: {
    color: theme.colors.textSecondary,
  },
  activateButton: {
    backgroundColor: theme.colors.urgency.high,
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.sm,
    borderRadius: theme.borderRadius.md,
  },
  activateText: {
    color: theme.colors.text,
    fontWeight: 'bold',
  },
});
