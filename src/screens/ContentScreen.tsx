import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/types';
import { ScreenContainer } from '../components/ScreenContainer';
import { contentApi } from '../api/client';
import YoutubeIframe from 'react-native-youtube-iframe';
import { theme } from '../theme/theme';
import { ContentAsset } from '../types';

type Props = NativeStackScreenProps<RootStackParamList, 'Content'>;

export const ContentScreen: React.FC<Props> = ({ route }) => {
  const { topicId } = route.params;
  const [assets, setAssets] = useState<ContentAsset[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchContent = async () => {
      try {
        const data = await contentApi.getTopicContent(topicId);
        setAssets(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchContent();
  }, [topicId]);

  const extractVideoId = (url: string) => {
    // Simple extraction for prototype
    const match = url.match(/[?&]v=([^&]+)/);
    return match ? match[1] : 'dQw4w9WgXcQ'; // Fallback Rickroll for prototype
  };

  return (
    <ScreenContainer loading={loading}>
      <ScrollView contentContainerStyle={styles.container}>
        {assets.map((asset) => (
          <View key={asset.id} style={styles.assetContainer}>
            <View style={styles.badge}>
              <Text style={styles.badgeText}>{asset.asset_type.toUpperCase()}</Text>
            </View>

            {asset.asset_type === 'video' && asset.content_url ? (
              <View style={styles.videoContainer}>
                <YoutubeIframe
                  height={200}
                  videoId={extractVideoId(asset.content_url)}
                />
              </View>
            ) : (
              <Text style={styles.contentText}>{asset.content_body}</Text>
            )}
          </View>
        ))}
        {assets.length === 0 && !loading && (
          <Text style={styles.emptyText}>No content available for this urgency tier.</Text>
        )}
      </ScrollView>
    </ScreenContainer>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: theme.spacing.md,
  },
  assetContainer: {
    backgroundColor: theme.colors.surface,
    padding: theme.spacing.md,
    borderRadius: theme.borderRadius.md,
    marginBottom: theme.spacing.lg,
  },
  badge: {
    alignSelf: 'flex-start',
    backgroundColor: theme.colors.primary,
    paddingHorizontal: theme.spacing.sm,
    paddingVertical: theme.spacing.xs,
    borderRadius: theme.borderRadius.sm,
    marginBottom: theme.spacing.md,
  },
  badgeText: {
    color: theme.colors.text,
    fontSize: theme.typography.caption.fontSize,
    fontWeight: 'bold',
  },
  contentText: {
    color: theme.colors.text,
    fontSize: theme.typography.body1.fontSize,
    lineHeight: 24,
  },
  videoContainer: {
    borderRadius: theme.borderRadius.md,
    overflow: 'hidden',
  },
  emptyText: {
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginTop: theme.spacing.xxl,
  },
});
