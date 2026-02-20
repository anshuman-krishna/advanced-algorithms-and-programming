def merge_intervals(intervals):
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    merged = []
    current = intervals[0]
    for i in range(1, len(intervals)):
        next_interval = intervals[i]
        if next_interval[0] <= current[1]:
            current[1] = max(current[1], next_interval[1])
        else:
            merged.append(current)
            current = next_interval
    merged.append(current)
    return merged
user_input = input("Enter intervals: ")
user_input = user_input.strip()[1:-1]
parts = user_input.split("],[")
intervals = []
for part in parts:
    part = part.replace("[", "").replace("]", "")
    start, end = part.split(",")
    intervals.append([int(start), int(end)])
result = merge_intervals(intervals)
print("Merged intervals:", result)
