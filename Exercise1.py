def ReverseInteger(n: int) -> int:
    reversed= 0
    while n > 0:
        digit = n % 10
        reversed= reversed * 10 + digit
        n = n // 10
    return reversed
num = int(input("Enter a non-negative integer: "))
result = ReverseInteger(num)
print("Reversed number:", result)
