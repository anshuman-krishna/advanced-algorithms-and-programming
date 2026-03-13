#two-pass
def first_unique(s):
    freq = {}
    for ch in s:
        if ch in freq:
            freq[ch] += 1
        else:
            freq[ch] = 1

    for i in range(len(s)):
        if freq[s[i]] == 1:
            return i
    return -1

#ordered-dictionary
def first_unique_ordered(s):
    freq = {}
    for i in range(len(s)):
        ch = s[i]
        if ch in freq:
            freq[ch] += 1
        else:
            freq[ch] = 1

    for i in range(len(s)):
        if freq[s[i]] == 1:
            return i
    return -1

if __name__ == "__main__":
    test_cases = [
        "leetcode",
        "loveleetcode",
        "aabb",
        "",
        "z",
        "ddccddbba"
    ]

    for s in test_cases:
        print("string:", s)
        print("two_pass:", first_unique(s))
        print("ordered:", first_unique_ordered(s))
        print()
