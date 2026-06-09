# algos we actually used and where

quick map of the data structures and algorithms from our labs to the features
they power in the app, plus the files they live in and a line on how we used
them. kept short on purpose. no fluff.

---

Hash Tables and Inverted Index (Lab 1, also researched online):
Powers the post search bar so a query like "beach husky" pulls every matching
post fast instead of scanning the whole table. we build a token to post id map
and layer tf-idf on top so the best matches float up. we looked the inverted
index approach up online to make a real multi keyword search viable.
files: backend/algorithms/inverted_index.py, backend/search/services.py,
backend/search/views.py (PostSearchView).

Set Operations and Similarity (Lab 2):
Mutual followers and "you both follow" use set intersection and difference.
the explore and reels recommendations use jaccard and cosine similarity over who
liked what, so we can suggest accounts and posts a user might actually like.
files: backend/algorithms/sets_ops.py, backend/algorithms/recommender.py,
backend/social/services.py, backend/search/services.py.

Doubly Linked List (Lab 3):
Runs the reels and stories swiping. each post is a node with prev and next, so
moving forward and back through the feed is constant time and we can jump to a
neighbour window around any post.
files: backend/algorithms/doubly_linked_list.py, backend/reels/services.py.

Queues and Priority Queues (Lab 3):
A plain fifo queue buffers incoming notifications (likes, comments, follows) and
a drain pass turns them into rows. replies jump the line through a priority lane.
the home feed is ranked with a priority queue keyed on our engagement score.
files: backend/algorithms/notification_queue.py,
backend/algorithms/priority_queue.py, backend/notifications/services.py,
backend/feed/services.py.

Priority Queues and Engagement Math (Lab 3):
Sorts the home feed with our own score, roughly (0.7 * likes) + (0.3 * recency),
with the like side log normalised so one viral post does not bury everything.
files: backend/algorithms/scoring.py, backend/algorithms/priority_queue.py,
backend/feed/services.py.

Recursive Comment Threads (Lab 4):
Comments are a recursive tree (each comment can have replies). we use recursion
to render the thread, to count total likes on a branch, and to prune deleted
comments. deep threads are walked with an explicit stack so a worker never blows
its recursion limit.
files: backend/algorithms/comment_thread.py,
backend/posts/services_threads.py.

Generalized Trees (Lab 5):
Organises the explore page. posts sit under a category hierarchy (cats and dogs
down to tabby, husky and so on) and we roll engagement up the tree bottom up, so
we can see a niche leaf or a whole branch.
files: backend/algorithms/category_tree.py, backend/search/services.py.

Graph, BFS and DFS (Lab 6):
The follow system is an adjacency list, not a matrix, since a matrix for a
billion users would need an absurd amount of ram. bfs finds the shortest
friendship chain between two people. dfs finds isolated communities so we can
recommend niche content.
files: backend/algorithms/follow_graph.py, backend/social/services.py.

Quadtree (Lab 7) [Spatial Data and Geolocation]:
Fetches posts near a location for the nearby tab. the quadtree splits the map
into sectors so a radius or bounding box query only touches the cells in the
user's area instead of every post. still tuning bucket size and depth.
files: backend/algorithms/quadtree.py, backend/geo/services.py.

Binary Search Tree (Lab 8):
Primary user index keyed by id for fast lookups, and the friend of friend
suggestions walk the bst ranking candidates by how many mutual connections they
share.
files: backend/algorithms/user_bst.py, backend/social/services.py.

Max Heap (Lab 8):
Runs the trending page. keeps the most popular posts at the top so we can pull
the top k without sorting the whole database every time.
files: backend/algorithms/max_heap.py, backend/feed/services.py.

Trie / Prefix Tree (Lab 8):
Username and hashtag autocomplete. as you type, the trie walks the prefix and
returns matches, weighted by post count for hashtags.
files: backend/algorithms/trie.py, backend/search/services.py.

Segment Tree (Lab 8) [Fast Analytics]:
Powers the insights range queries. one segment tree per user over their likes by
day, plus a second one over comments by day, lets us answer "likes or comments
between these two dates" and "best single day" in log time. still reading up on
more range query ideas.
files: backend/algorithms/segment_tree.py, backend/analytics/services.py.
