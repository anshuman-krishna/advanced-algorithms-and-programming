# instagram backend, built on the algorithms we learned in class

we are building a functional, backend heavy clone of instagram for our advanced
algorithms and programming course. the goal is not to ship a polished consumer
product. the goal is to take every data structure and algorithm from our eight
lab folders and put it to work in a real distributed system shaped problem:
ranking a feed, mapping a follow graph, threading comments, suggesting friends,
serving search, and so on.

the visual layer is intentionally plain. white background, black text, a thin
brand colored border here and there. we want the algorithms to be the thing
you notice when you click around.

## what we are building

a django backend that exposes a rest api for users, posts, likes, comments,
follows, search, recommendations, notifications, and reels, plus a tiny expo
react native frontend that drives those endpoints.

the backend is structured so that each algorithmic primitive lives in its own
file under `backend/algorithms/` and is unit tested in isolation. the django
apps then compose those primitives:

- **lab 1 (hash tables, arrays)** powers the inverted index search and
  pagination slicing.
- **lab 2 (sets, jaccard, cosine)** powers mutual followers and the reels
  recommender.
- **lab 3 (linked lists, queues, priority queues)** powers the reels swipe
  cursor, the notification fanout, and the local feed ranker.
- **lab 4 (recursion, divide and conquer, iterative stacks)** powers the
  nested comment threads, total likes aggregation, and deep tree pruning.
- **lab 5 (generalized trees)** powers the explore page taxonomy and bottom
  up engagement rollups.
- **lab 6 (graphs, bfs, dfs)** powers the follow graph, shortest friendship
  chain, and community detection.
- **lab 7 (spatial)** is reserved for the quadtree work on geo tagged posts.
- **lab 8 (bsts, heaps, tries, segment trees)** powers user indexing,
  trending feeds, autocomplete, and analytics range queries.

every feature carries a comment pointing back at the lab and exercise number
that inspired it, so it is always traceable to the coursework.

## repo layout

```
backend/                 django project
  algorithms/            pure python data structures (no django imports)
    tests/               unit tests for every primitive
  accounts/              user model, auth, profile endpoints
  posts/                 post / comment / like models, comment thread service
  social/                follow graph, mutuals, friend of friend
  feed/                  home feed, trending heap, priority queue ranker
  search/                inverted index, tries, recommender, category tree
  notifications/         lab 3 queue persisted into Notification rows
  reels/                 dll backed reels cursor + view tracking
  analytics/             lab 8 segment tree per user, range likes endpoints
  geo/                   lab 7 quadtree, nearby / bbox / nearest endpoints
  config/                django settings and root urls
  manage.py
frontend/                expo react native app
  src/api/client.js      fetch wrapper, all endpoints in one place
  src/screens/           home, reels, trending, search, notifs, thread
  src/theme/             single palette file
README.md                this file
```

## getting it running locally

we keep dev as boring as possible. sqlite by default, postgres only when you
flip an env var.

### 1. clone and create a virtualenv

```
git clone <repo>
cd advanced-algorithms-and-programming/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. apply migrations and seed a tiny demo network

```
python manage.py migrate
python manage.py seed_demo
python manage.py seed_categories
python manage.py seed_geo
python manage.py rebuild_search_index
python manage.py warm_reels
```

at this point we have five users, a handful of posts, a follow graph, the
explore tree, the inverted index hot, the reels doubly linked list warm, and
geo coordinates attached to every demo post so the quadtree returns real data.

### 3. start the api

```
python manage.py runserver
```

the api now lives at `http://127.0.0.1:8000/api/`. swing by `/api/posts/posts/`
or `/api/feed/trending/?k=10` in a browser to verify.

### 4. run the frontend

in a second terminal:

```
cd ../frontend
npm install
npm run start
```

scan the qr code with the expo go app, or press `w` to open the web preview.
the tabs across the top hop between home, reels, trending, search,
notifications, and the thread viewer.

if the phone or simulator cannot reach `127.0.0.1`, set `EXPO_PUBLIC_API_BASE`
to a lan ip before starting expo, for example
`EXPO_PUBLIC_API_BASE=http://192.168.1.42:8000 npm run start`.

### 5. (optional) switch the database to postgres

create a `.env` file in `backend/`:

```
USE_POSTGRES=1
POSTGRES_DB=instagram_clone
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
```

then re-run `python manage.py migrate`. nothing else changes.

## running the tests

every algorithm has its own unit test file under `backend/algorithms/tests/`.
no django bootstrap needed, they run on plain `unittest`:

```
cd backend
python -m unittest discover -s algorithms/tests
```

we expect every test to be green before merging.

## ops cheatsheet

a few management commands we use during development and demos:

- `python manage.py seed_demo` rebuilds the demo users, posts, and follows.
- `python manage.py seed_categories` builds the lab 5 explore taxonomy.
- `python manage.py seed_geo` round-robins city coordinates onto demo posts
  so the lab 7 quadtree has something to query.
- `python manage.py rebuild_search_index` resets the inverted index, user
  trie, and hashtag trie from the database.
- `python manage.py warm_reels --window 200` rehydrates the reels dll.
- `python manage.py drain_notifications --loop --interval 5` runs the
  background drainer for the lab 3 notification queue.

## conventions

- comments in code are minimal and lowercase.
- every file that implements a feature names the lab and exercise it
  references at the top.
- the frontend stays plain. no animations, no icon libraries, no design
  systems. white, black, and the instagram blue for accents.

## status

the project tracker lives in our internal `testing/todos.md` (gitignored).
see git log for the public timeline of phases shipped so far.
