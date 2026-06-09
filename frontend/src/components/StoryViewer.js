// story viewer. opened by tapping a story ring on the home feed. shows each
// user's most recent post as their story. tap the right half to advance, the
// left half to go back, the avatar to open that user's profile, and back to
// close. there is no separate stories table, so a story is simply that user's
// latest post image and caption.
import React, { useCallback, useEffect, useState } from 'react';
import {
  Image,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

import { api } from '../api/client';
import { useApp } from '../context/AppContext';
import AvatarRing from './AvatarRing';
import OverlayFrame from './OverlayFrame';
import { spacing, typography } from '../theme';

export default function StoryViewer({ users = [], index = 0 }) {
  const { openProfile, closeTop } = useApp();
  const [pos, setPos] = useState(index);
  const [story, setStory] = useState(null);
  const [loading, setLoading] = useState(true);

  const current = users[pos];

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setStory(null);
    if (!current) return undefined;
    api
      .userPosts(current.id)
      .then((res) => {
        if (cancelled) return;
        const list = res.results || res || [];
        setStory(list[0] || null);
      })
      .catch(() => undefined)
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [current]);

  const next = useCallback(() => {
    if (pos + 1 < users.length) setPos((p) => p + 1);
    else closeTop();
  }, [pos, users.length, closeTop]);

  const prev = useCallback(() => {
    if (pos > 0) setPos((p) => p - 1);
  }, [pos]);

  if (!current) {
    return <OverlayFrame title="story" onBack={closeTop} dark><View /></OverlayFrame>;
  }

  return (
    <OverlayFrame title={`@${current.username}`} onBack={closeTop} dark>
      <View style={styles.wrap}>
        {/* progress segments */}
        <View style={styles.segments}>
          {users.map((u, i) => (
            <View
              key={u.id}
              style={[styles.segment, i <= pos ? styles.segmentOn : styles.segmentOff]}
            />
          ))}
        </View>
        <Pressable style={styles.userTap} onPress={() => openProfile(current.username)}>
          <AvatarRing username={current.username} imageUrl={current.avatar} size={40} />
          <Text style={[typography.bodyStrong, styles.userName]}>@{current.username}</Text>
        </Pressable>

        <View style={styles.stage}>
          {story?.image ? (
            <Image source={{ uri: story.image }} style={styles.media} resizeMode="cover" />
          ) : (
            <LinearGradient
              colors={['#feda75', '#fa7e1e', '#d62976', '#962fbf']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={styles.media}
            >
              <Text style={styles.glyph}>{current.username.slice(0, 1).toUpperCase()}</Text>
            </LinearGradient>
          )}
          {story?.caption ? (
            <View style={styles.captionWrap}>
              <Text style={styles.caption} numberOfLines={3}>
                {story.caption}
              </Text>
            </View>
          ) : !loading && !story ? (
            <View style={styles.captionWrap}>
              <Text style={styles.caption}>no story yet</Text>
            </View>
          ) : null}

          {/* tap zones */}
          <Pressable style={styles.left} onPress={prev} />
          <Pressable style={styles.right} onPress={next} />
        </View>
      </View>
    </OverlayFrame>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: '#000' },
  segments: { flexDirection: 'row', paddingHorizontal: spacing.md, paddingTop: spacing.sm },
  segment: { flex: 1, height: 3, marginHorizontal: 2, borderRadius: 2 },
  segmentOn: { backgroundColor: '#ffffff' },
  segmentOff: { backgroundColor: 'rgba(255,255,255,0.3)' },
  userTap: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
  },
  userName: { color: '#fff', marginLeft: spacing.md },
  stage: { flex: 1, position: 'relative' },
  media: { ...StyleSheet.absoluteFillObject, alignItems: 'center', justifyContent: 'center' },
  glyph: { fontSize: 160, color: 'rgba(255,255,255,0.2)', fontWeight: '700' },
  captionWrap: {
    position: 'absolute',
    left: spacing.lg,
    right: spacing.lg,
    bottom: spacing.xxl,
  },
  caption: { color: '#fff', fontSize: 16, fontWeight: '600' },
  left: { position: 'absolute', left: 0, top: 0, bottom: 0, width: '35%' },
  right: { position: 'absolute', right: 0, top: 0, bottom: 0, width: '65%' },
});
