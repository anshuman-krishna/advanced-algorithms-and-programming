// renders the overlay stack. each overlay is a full screen opaque surface, so
// later entries naturally cover earlier ones and going back just pops the top.
import React from 'react';

import PostDetailModal from './PostDetailModal';
import ProfileModal from './ProfileModal';
import HashtagModal from './HashtagModal';
import StoryViewer from './StoryViewer';

export default function OverlayHost({ stack }) {
  if (!stack || stack.length === 0) return null;
  return stack.map((o) => {
    switch (o.type) {
      case 'post':
        return <PostDetailModal key={o.id} postId={o.postId} post={o.post} />;
      case 'profile':
        return <ProfileModal key={o.id} identifier={o.identifier} />;
      case 'hashtag':
        return <HashtagModal key={o.id} tag={o.tag} />;
      case 'story':
        return <StoryViewer key={o.id} users={o.users} index={o.index} />;
      default:
        return null;
    }
  });
}
