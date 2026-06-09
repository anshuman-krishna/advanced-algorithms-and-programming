// login prompt. shows up when an action needs a signed in user (commenting,
// liking, following, notifications) instead of letting a raw 401 reach the ui.
// plain username and password against /api/auth/token/.
import React, { useState } from 'react';
import {
  KeyboardAvoidingView,
  Modal,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { colors, radii, spacing, typography } from '../theme';
import GradientButton from './GradientButton';
import GradientText from './GradientText';
import OutlineButton from './OutlineButton';

export default function LoginModal({ visible, onSubmit, onClose, busy, error }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const submit = () => {
    if (!username.trim() || !password) return;
    onSubmit(username.trim(), password);
  };

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onClose}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={styles.backdrop}
      >
        <View style={styles.card}>
          <GradientText style={[typography.title, styles.title]}>welcome back</GradientText>
          <Text style={[typography.body, styles.subtitle]}>
            you are not logged in. please log in to continue.
          </Text>

          <TextInput
            value={username}
            onChangeText={setUsername}
            placeholder="username"
            placeholderTextColor={colors.muted}
            autoCapitalize="none"
            autoCorrect={false}
            style={styles.input}
          />
          <TextInput
            value={password}
            onChangeText={setPassword}
            placeholder="password"
            placeholderTextColor={colors.muted}
            secureTextEntry
            autoCapitalize="none"
            style={styles.input}
            onSubmitEditing={submit}
          />

          {error ? <Text style={styles.error}>{error}</Text> : null}

          <View style={styles.actions}>
            <GradientButton label={busy ? 'logging in' : 'log in'} onPress={submit} disabled={busy} />
            <OutlineButton label="not now" onPress={onClose} />
          </View>

          <Pressable onPress={() => { setUsername('alice'); setPassword('password123'); }}>
            <Text style={styles.hint}>demo account: alice / password123 (tap to fill)</Text>
          </Pressable>
        </View>
      </KeyboardAvoidingView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: colors.scrim,
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.xl,
  },
  card: {
    width: '100%',
    maxWidth: 360,
    backgroundColor: colors.background,
    borderRadius: radii.lg,
    padding: spacing.xl,
    borderWidth: 1,
    borderColor: colors.border,
  },
  title: { marginBottom: spacing.xs },
  subtitle: { color: colors.muted, marginBottom: spacing.lg },
  input: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radii.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    marginBottom: spacing.md,
    color: colors.text,
    backgroundColor: colors.inputBackground,
  },
  error: { color: colors.primary, marginBottom: spacing.md },
  actions: { gap: spacing.sm, marginTop: spacing.xs },
  hint: {
    ...typography.caption,
    color: colors.muted,
    marginTop: spacing.lg,
    textAlign: 'center',
  },
});
