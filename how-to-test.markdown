# how to run and test the whole project

this is the plain end to end guide for getting the project up and checking that every
part works. it covers the backend, the frontend, the test suites, and a curl walk through
of every endpoint group. no prior context needed, just follow it top to bottom.

everything defaults to sqlite so you do not need postgres to try it. postgres is a single
env flag at the end if you want it.

## what you need first

- python 3.11 or newer
- node 18 or newer and npm, only needed for the frontend
- git
- optional, postgres 14 or newer if you want to swap off sqlite

## 1. backend setup

from the repo root:

```
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

apply the migrations and seed a small demo network so nothing comes back empty:

```
python manage.py migrate
python manage.py seed_demo
python manage.py seed_categories
python manage.py seed_geo
python manage.py rebuild_search_index
python manage.py warm_reels
```

after that you have five demo users (alice, bob, carol, dave, eve, all with the password
password123), a handful of posts, a follow graph, the explore category tree, the inverted
index hot, the reels doubly linked list warm, and city coordinates on the demo posts so
the geo quadtree returns real data.

start the server:

```
python manage.py runserver
```

the api now lives at http://127.0.0.1:8000/api/. open http://127.0.0.1:8000/api/posts/posts/
or http://127.0.0.1:8000/api/feed/trending/?k=10 in a browser and you should see json.

## 2. getting an auth token

reads are open to everyone, so you can browse most things without logging in. writes
(liking, commenting, following) need a token. grab one like this:

```
curl -s -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "password123"}'
```

that returns `{"token": "..."}`. for any write call below, send it as a header:

```
-H "Authorization: Token <paste the token here>"
```

## 3. walking through every endpoint group

most of these are open reads. a few key off the logged in user and need a token, those
are called out as you go. the point is to confirm each algorithm path returns data.

### accounts and posts (crud)

```
curl -s http://127.0.0.1:8000/api/accounts/users/
curl -s http://127.0.0.1:8000/api/posts/posts/
curl -s http://127.0.0.1:8000/api/posts/posts/1/
```

### feed ranking (lab 3 priority queue, lab 8 max heap)

trending and explore are open. the personal home feed needs a token since it ranks against
who you follow:

```
curl -s "http://127.0.0.1:8000/api/feed/trending/?k=10&window_hours=168"
curl -s "http://127.0.0.1:8000/api/feed/explore/?category=1&k=10"
curl -s "http://127.0.0.1:8000/api/feed/home/?offset=0&limit=10&window_hours=168" \
  -H "Authorization: Token <token>"
```

the home feed payload carries a per post `score_breakdown` so you can see why each post
ranked where it did.

### search and explore (lab 1 inverted index, lab 8 trie, lab 5 generalized tree)

```
curl -s "http://127.0.0.1:8000/api/search/posts/?q=lisbon"
curl -s "http://127.0.0.1:8000/api/search/autocomplete/users/?q=al"
curl -s "http://127.0.0.1:8000/api/search/autocomplete/hashtags/?q=co"
curl -s "http://127.0.0.1:8000/api/search/hashtags/trending/?limit=10"
curl -s http://127.0.0.1:8000/api/search/explore/
```

recommendations and the index stats both need a token (the recommender keys off the
logged in user):

```
curl -s "http://127.0.0.1:8000/api/search/recommendations/?strategy=jaccard&limit=10" \
  -H "Authorization: Token <token>"
curl -s http://127.0.0.1:8000/api/search/stats/ -H "Authorization: Token <token>"
```

### social graph (lab 6 graph, lab 2 sets, lab 8 bst)

these are open:

```
curl -s http://127.0.0.1:8000/api/social/communities/
curl -s "http://127.0.0.1:8000/api/social/shortest-chain/?from=alice&to=eve"
curl -s http://127.0.0.1:8000/api/social/users/alice/community/
curl -s http://127.0.0.1:8000/api/social/users/alice/niche-posts/
curl -s "http://127.0.0.1:8000/api/social/users/alice/reach/?max_depth=3"
curl -s http://127.0.0.1:8000/api/social/users/alice/followers/
curl -s http://127.0.0.1:8000/api/social/relationship/alice/bob/
```

the graph stats and the friend suggestions need a token:

```
curl -s http://127.0.0.1:8000/api/social/graph/stats/ -H "Authorization: Token <token>"
curl -s "http://127.0.0.1:8000/api/social/suggestions/?user=1" -H "Authorization: Token <token>"
```

to follow someone (write, needs a token):

```
curl -s -X POST http://127.0.0.1:8000/api/social/follows/ \
  -H "Authorization: Token <token>" \
  -H "Content-Type: application/json" \
  -d '{"following": 2}'
```

### comment threads (lab 4 recursion, divide and conquer, iterative stack)

```
curl -s http://127.0.0.1:8000/api/posts/posts/1/thread/
curl -s http://127.0.0.1:8000/api/posts/posts/1/thread-stats/
curl -s "http://127.0.0.1:8000/api/posts/posts/1/thread-search/?q=nice"
curl -s http://127.0.0.1:8000/api/posts/posts/1/thread-depth/
curl -s http://127.0.0.1:8000/api/posts/posts/1/thread-count/
```

### reels (lab 3 doubly linked list)

```
curl -s "http://127.0.0.1:8000/api/reels/page/?cursor=&direction=next&limit=5"
curl -s "http://127.0.0.1:8000/api/reels/around/1/?k=2"
curl -s http://127.0.0.1:8000/api/reels/most-viewed/
curl -s http://127.0.0.1:8000/api/reels/stats/
```

mark a reel viewed (write):

```
curl -s -X POST http://127.0.0.1:8000/api/reels/1/view/ -H "Authorization: Token <token>"
```

### notifications (lab 3 queue)

both of these need a token:

```
curl -s http://127.0.0.1:8000/api/notifications/queue/stats/ -H "Authorization: Token <token>"
curl -s http://127.0.0.1:8000/api/notifications/ -H "Authorization: Token <token>"
```

drain the background queue from the cli:

```
python manage.py drain_notifications --max
```

### analytics (lab 8 segment tree)

```
curl -s "http://127.0.0.1:8000/api/analytics/users/alice/likes-range/?from=2026-01-01&to=2026-12-31"
curl -s http://127.0.0.1:8000/api/analytics/users/alice/likes-series/
curl -s http://127.0.0.1:8000/api/analytics/stats/
```

### geo (lab 7 quadtree)

```
curl -s "http://127.0.0.1:8000/api/geo/nearby/?lat=38.72&lng=-9.14&radius=50&unit=km"
curl -s "http://127.0.0.1:8000/api/geo/bbox/?min_lat=30&min_lng=-15&max_lat=45&max_lng=5"
curl -s "http://127.0.0.1:8000/api/geo/nearest/?lat=38.72&lng=-9.14&k=3"
curl -s "http://127.0.0.1:8000/api/geo/dense/?threshold=2&min_size=2"
curl -s http://127.0.0.1:8000/api/geo/stats/
```

### ops dashboard (everything in one payload, good for the demo)

```
curl -s http://127.0.0.1:8000/api/ops/dashboard/
```

this rolls up the search index stats, the trending heap state, the reels list size, the
follow graph metrics, the bst stats, the analytics tree count, the geo quadtree size, the
notification queue counters, and category coverage in one response.

heads up: this endpoint currently returns a 500 because it calls `len()` on the trending
heap, which has a `.size()` method but no `__len__`. it is the first item in the loose
ends list in `testing/new-updates.md`, the fix is a one line swap to `heap.size()`.

## 4. frontend

in a second terminal, from the repo root:

```
cd frontend
npm install
npm run start
```

scan the qr code with the expo go app, or press w for the web preview. the tabs across
the top hop between home, reels, trending, search, notifications, thread, nearby, stats,
and graph. each tab drives the matching api group above.

if the phone or simulator cannot reach 127.0.0.1, point expo at your lan ip first:

```
EXPO_PUBLIC_API_BASE=http://192.168.1.42:8000 npm run start
```

## 5. running the test suites

two suites. the algorithm primitives run on plain unittest with no django bootstrap:

```
cd backend
source .venv/bin/activate
python -m unittest discover -s algorithms/tests
```

the django side covers the viewsets, signals, rate limiter, and cache lifecycles. set the
warmup flag so the background cache loaders do not race the test run:

```
AAP_DISABLE_WARMUP=1 python manage.py test
```

current baseline is 384 green, 181 from the algorithm suite and 203 from the django suite.
everything should be green before you commit.

## 6. ops and warm up commands

these are the management commands used during development and demos:

- `python manage.py seed_demo` rebuilds the demo users, posts, and follows.
- `python manage.py seed_categories` builds the lab 5 explore taxonomy.
- `python manage.py seed_geo` puts city coordinates on the demo posts for the quadtree.
- `python manage.py rebuild_search_index` resets the inverted index and both tries.
- `python manage.py rebuild_caches` resets the adjacency list, bst, reels list, trending
  heap, search index, analytics segment trees, and geo quadtree in one shot.
- `python manage.py warm_reels --window 200` rehydrates the reels list.
- `python manage.py warm_trending` pre builds the trending heap.
- `python manage.py warm_analytics` builds the segment tree for every active user.
- `python manage.py warm_threads <post_id>` pre builds one comment tree.
- `python manage.py drain_notifications --loop --interval 5` runs the queue drainer.

## 7. optional, switch to postgres

create a `.env` file inside `backend/`:

```
USE_POSTGRES=1
POSTGRES_DB=instagram_clone
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
```

then re run `python manage.py migrate` and the seed commands from step 1. nothing else
changes, the same endpoints and the same tests work.

## 8. note on work in progress

labs 9 and 10 were imported into `LABS/LAB_09_HardProblems` and
`LABS/LAB_10_BT_OPT_DP_GA`. the features that build on them (the `/api/optimize/` group:
minimum influencer set, conflict free labeling, the campaign budget optimizer, the non
conflicting set, and the balanced group split) are tracked in `testing/new-updates.md`
and are not wired up yet. once each chunk lands it gets its own curl block in section 3
and its own test file under `backend/algorithms/tests/`.
