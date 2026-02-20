def IsBalanced(s: str) -> bool:
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack:   
                return False
            top = stack.pop()
            if pairs[ch] != top:
                return False
    return len(stack) == 0
stacks = input("Enter a string with brackets (): [] {} : ")
result = IsBalanced(stacks)
print("Balanced?" , result)
