import React, { useCallback, useEffect, useState } from 'react';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { FlatList, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { ResizeMode, Video } from 'expo-av';
import YoutubePlayer from 'react-native-youtube-iframe';
import ScreenContainer from '../components/ScreenContainer';
import LoadingView from '../components/LoadingView';
import ErrorView from '../components/ErrorView';
import { theme } from '../theme/theme';
import { RootStackParamList } from '../navigation/types';
import { fetchTopicContent } from '../api/topics';
import { markTopicComplete } from '../api/progress';
import { DenseContent, FastContent, ShortVideoContent, TopicContent } from '../types';

type Props = NativeStackScreenProps<RootStackParamList, 'Content'>;

export default function ContentScreen({ route, navigation }: Props) {
  const { topicId, topicTitle, mode } = route.params;
  const [content, setContent] = useState<TopicContent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [completing, setCompleting] = useState(false);
  const [completed, setCompleted] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchTopicContent(topicId, mode);
      setContent(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not load this content.');
    } finally {
      setLoading(false);
    }
  }, [topicId, mode]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleComplete() {
    setCompleting(true);
    try {
      await markTopicComplete(topicId, mode);
      setCompleted(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not save your progress.');
    } finally {
      setCompleting(false);
    }
  }

  return (
    // Panic Toggle intentionally hidden here: visible up until — not
    // during — the active learning/content-consumption flow.
    <ScreenContainer showPanicToggle={false}>
      <View style={styles.header}>
        <Pressable onPress={() => navigation.goBack()} hitSlop={12}>
          <Text style={styles.back}>{'\u2190'} Back</Text>
        </Pressable>
        <Text style={styles.title} numberOfLines={1}>
          {topicTitle}
        </Text>
      </View>

      {loading && <LoadingView label="Loading content…" />}
      {!loading && error && <ErrorView message={error} onRetry={load} />}

      {!loading && !error && content?.mode === 'dense' && <DenseContentView content={content} />}
      {!loading && !error && content?.mode === 'fast' && <FastContentView content={content} />}
      {!loading && !error && content?.mode === 'short_video' && (
        <ShortVideoContentView content={content} />
      )}

      {!loading && !error && content && (
        <View style={styles.footer}>
          <Pressable
            style={[styles.completeButton, completed && styles.completeButtonDone]}
            onPress={handleComplete}
            disabled={completing || completed}
          >
            <Text style={styles.completeLabel}>
              {completed ? 'Marked complete ✓' : completing ? 'Saving…' : 'Mark Complete'}
            </Text>
          </Pressable>
        </View>
      )}
    </ScreenContainer>
  );
}

function getYoutubeId(url: string): string {
  const match = url.match(/(?:v=|youtu\.be\/|embed\/)([\w-]{11})/);
  return match ? match[1] : url;
}

function DenseContentView({ content }: { content: DenseContent }) {
  return (
    <ScrollView contentContainerStyle={styles.body}>
      <Section title="Prerequisites">
        {content.prerequisites.map((p, i) => (
          <Text key={i} style={styles.listItem}>
            {'\u2022'} {p}
          </Text>
        ))}
      </Section>

      <Section title="Recommended textbooks">
        {content.textbooks.map((t, i) => (
          <Text key={i} style={styles.listItem}>
            {t.title} — {t.author}
          </Text>
        ))}
      </Section>

      <Section title="Notes">
        <Text style={styles.notes}>{content.notes}</Text>
      </Section>

      <Section title="Lecture video">
        <YoutubePlayer height={210} videoId={getYoutubeId(content.videoUrl)} />
      </Section>
    </ScrollView>
  );
}

function FastContentView({ content }: { content: FastContent }) {
  return (
    <ScrollView contentContainerStyle={styles.body}>
      <Section title="Key points">
        {content.bullets.map((b, i) => (
          <Text key={i} style={styles.listItem}>
            {'\u2022'} {b}
          </Text>
        ))}
      </Section>

      <Section title="Must-ask topics">
        <View style={styles.tagRow}>
          {content.mustAskTopics.map((t, i) => (
            <View key={i} style={styles.tag}>
              <Text style={styles.tagLabel}>{t}</Text>
            </View>
          ))}
        </View>
      </Section>

      <Section title="Quick video">
        <YoutubePlayer height={210} videoId={getYoutubeId(content.videoUrl)} />
      </Section>
    </ScrollView>
  );
}

function ShortVideoContentView({ content }: { content: ShortVideoContent }) {
  return (
    <FlatList
      data={content.videos}
      keyExtractor={(item) => item.id}
      pagingEnabled
      showsVerticalScrollIndicator={false}
      renderItem={({ item }) => (
        <View style={styles.shortSlide}>
          <Video
            source={{ uri: item.url }}
            style={StyleSheet.absoluteFillObject}
            resizeMode={ResizeMode.COVER}
            isLooping
            shouldPlay
            useNativeControls={false}
          />
          <View style={styles.shortCaptionWrap}>
            <Text style={styles.shortCaption}>{item.caption}</Text>
          </View>
        </View>
      )}
    />
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: theme.spacing(6),
    paddingBottom: theme.spacing(3),
  },
  back: { color: theme.color.accent, fontWeight: '600', marginRight: theme.spacing(4) },
  title: { ...theme.font.subheading, color: theme.color.textPrimary, flexShrink: 1 },
  body: { padding: theme.spacing(6), paddingBottom: theme.spacing(12) },
  section: { marginBottom: theme.spacing(6) },
  sectionTitle: { ...theme.font.subheading, color: theme.color.textPrimary, marginBottom: theme.spacing(2) },
  listItem: { ...theme.font.body, color: theme.color.textMuted, marginBottom: theme.spacing(1) },
  notes: { ...theme.font.body, color: theme.color.textMuted, lineHeight: 22 },
  tagRow: { flexDirection: 'row', flexWrap: 'wrap' },
  tag: {
    backgroundColor: theme.color.accentMuted,
    borderRadius: theme.radius.pill,
    paddingHorizontal: theme.spacing(3),
    paddingVertical: theme.spacing(1),
    marginRight: theme.spacing(2),
    marginBottom: theme.spacing(2),
  },
  tagLabel: { color: theme.color.accent, fontWeight: '600', fontSize: 12 },
  footer: { padding: theme.spacing(6) },
  completeButton: {
    backgroundColor: theme.color.accent,
    borderRadius: theme.radius.md,
    paddingVertical: theme.spacing(3),
    alignItems: 'center',
  },
  completeButtonDone: { backgroundColor: theme.color.success },
  completeLabel: { color: theme.color.background, fontWeight: '700' },
  shortSlide: {
    // Approximate one-screen height for the prototype. Swap for
    // Dimensions.get('window').height in production so it's exact on
    // every device.
    height: 640,
    justifyContent: 'flex-end',
    backgroundColor: '#000',
  },
  shortCaptionWrap: { padding: theme.spacing(6) },
  shortCaption: { color: '#fff', fontWeight: '600', fontSize: 15 },
});
