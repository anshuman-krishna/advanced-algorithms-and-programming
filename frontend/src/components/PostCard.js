import React from 'react';
import { Image, StyleSheet, Text, View } from 'react-native';

import { colors } from '../theme/colors';

export default function PostCard({ post }) {
  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.username}>{post.author?.username ?? 'unknown'}</Text>
      </View>
      {post.image ? (
        <Image source={{ uri: post.image }} style={styles.image} resizeMode="cover" />
      ) : (
        <View style={styles.imagePlaceholder} />
      )}
      <View style={styles.body}>
        <Text style={styles.caption}>{post.caption}</Text>
        <Text style={styles.meta}>
          {post.like_count} likes · {post.comment_count} comments
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.background,
    borderColor: colors.border,
    borderWidth: 1,
    marginBottom: 12,
  },
  header: { padding: 10, borderBottomColor: colors.border, borderBottomWidth: 1 },
  username: { color: colors.text, fontWeight: '600' },
  image: { width: '100%', aspectRatio: 1 },
  imagePlaceholder: {
    width: '100%',
    aspectRatio: 1,
    backgroundColor: colors.background,
    borderTopColor: colors.border,
    borderBottomColor: colors.border,
    borderTopWidth: 1,
    borderBottomWidth: 1,
  },
  body: { padding: 10 },
  caption: { color: colors.text, marginBottom: 6 },
  meta: { color: colors.muted, fontSize: 12 },
});
