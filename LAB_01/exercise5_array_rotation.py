#temporary-array
def rotate_temp(vect, k):
    n = len(vect)
    if n == 0:
        return vect
    k %= n
    temp = vect[n - k:] + vect[:n - k]
    return temp

#one-by-one
def rotate_one_by_one(vect, k):
    n = len(vect)
    if n == 0:
        return vect
    k %= n
    for _ in range(k):
        last = vect[-1]
        for j in range(n - 1, 0, -1):
            vect[j] = vect[j - 1]
        vect[0] = last
    return vect

#reverse-segments
def rotate_reverse(vect, k):
    n = len(vect)
    if n == 0:
        return vect
    k %= n
    def reverse(arr, left, right):
        while left < right:
            arr[left], arr[right] = arr[right], arr[left]
            left += 1
            right -= 1
    reverse(vect, 0, n - 1)
    reverse(vect, 0, k - 1)
    reverse(vect, k, n - 1)
    return vect

if __name__ == "__main__":
    test_cases = [
        ([1, 2, 3, 4, 5, 6, 7], 3),
        ([1], 5),
        ([], 4),
        ([1, 2], 0),
        ([1, 2, 3], 10)
    ]

    for arr, k in test_cases:
        print("original:", arr, "k:", k)
        print("temp:", rotate_temp(arr.copy(), k))
        print("one_by_one:", rotate_one_by_one(arr.copy(), k))
        print("reverse:", rotate_reverse(arr.copy(), k))
        print()
