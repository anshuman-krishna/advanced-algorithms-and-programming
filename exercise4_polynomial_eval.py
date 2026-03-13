def evaluate_polynomial(coeffs, x):
    result = 0
    for i in range(len(coeffs) - 1, -1, -1):
        result = result * x + coeffs[i]
    return result

if __name__ == "__main__":
    test_cases = [
        ([3, -2, 0, 5], 2),
        ([1], 10),
        ([0, 0, 0], 5),
        ([-1, 1], 3),
        ([], 2)
    ]

    for coeffs, x in test_cases:
        if len(coeffs) == 0:
            print("empty polynomial -> undefined")
        else:
            print(evaluate_polynomial(coeffs, x))
