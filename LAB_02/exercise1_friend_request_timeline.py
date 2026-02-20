def analyze_message(message):
    uppercase_letters = 0
    punctuation_marks = 0
    total_letters = 0
    previous_character = None
    consecutive_count = 1

    for character in message:
        if character.isalpha():
            total_letters += 1
            if character.isupper():
                uppercase_letters += 1
        if character in ['!', '?']:
            punctuation_marks += 1
        if character == previous_character:
            consecutive_count += 1
            if consecutive_count > 3:
                repeated_detected = True
        else:
            consecutive_count = 1
        previous_character = character
    if total_letters == 0:
        caps_ratio = 0
    else:
        caps_ratio = uppercase_letters / total_letters
    if caps_ratio >= 0.6 or punctuation_marks >= 5:
        sentiment = "AGGRESSIVE"
    elif caps_ratio >= 0.3 or punctuation_marks >= 3:
        sentiment = "URGENT"
    else:
        sentiment = "CALM"
    return {
        "Uppercase Letters": uppercase_letters,
        "Punctuation Count": punctuation_marks,
        "Caps Ratio": round(caps_ratio, 2),
        "Classification": sentiment
    }

user_message = input("Enter friend request message: ")
analysis = analyze_message(user_message)
print("\nMessage Analysis:")
for key, value in analysis.items():
    print(f"{key}: {value}")
