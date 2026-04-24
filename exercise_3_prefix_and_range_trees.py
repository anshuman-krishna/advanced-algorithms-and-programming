class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.user_id = None


class Trie:
    def __init__(self):
        self.root = TrieNode()

   
    def insert(self, username, user_id):
        node = self.root
        for ch in username:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True
        node.user_id = user_id

    def search(self, username):
        node = self.root
        for ch in username:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node.user_id if node.is_end else None
    def starts_with(self, prefix):
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True

    def autocomplete(self, prefix, max_results):
        results = []
        node = self.root

        for ch in prefix:
            if ch not in node.children:
                return results
            node = node.children[ch]

        self._collect_words(node, prefix, results, max_results)
        return results

    def _collect_words(self, node, current_word, results, max_results):
        if len(results) >= max_results:
            return

        if node.is_end:
            results.append((current_word, node.user_id))

        for ch in node.children:
            self._collect_words(node.children[ch], current_word + ch, results, max_results)

   
    def delete(self, username):
        self._delete(self.root, username, 0)

    def _delete(self, node, username, index):
        if not node:
            return False

        if index == len(username):
            if not node.is_end:
                return False
            node.is_end = False
            return len(node.children) == 0

        ch = username[index]
        if ch not in node.children:
            return False

        should_delete = self._delete(node.children[ch], username, index + 1)

        if should_delete:
            del node.children[ch]
            return len(node.children) == 0 and not node.is_end

        return False