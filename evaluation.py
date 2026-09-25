from workflow import classify_message


TEST_CASES = [
    {
        "message": "Thank you for fixing my credit card issue.",
        "expected": "POSITIVE_FEEDBACK"
    },
    {
        "message": "Thanks for helping me reset my password.",
        "expected": "POSITIVE_FEEDBACK"
    },
    {
        "message": "Your team was very helpful. Thank you!",
        "expected": "POSITIVE_FEEDBACK"
    },
    {
        "message": "I really appreciate your help with my account.",
        "expected": "POSITIVE_FEEDBACK"
    },

    {
        "message": "My debit card replacement still hasn't arrived.",
        "expected": "NEGATIVE_FEEDBACK"
    },
    {
        "message": "I am frustrated because my account is still locked.",
        "expected": "NEGATIVE_FEEDBACK"
    },
    {
        "message": "This problem has not been resolved.",
        "expected": "NEGATIVE_FEEDBACK"
    },
    {
        "message": "I was charged twice and nobody has helped me.",
        "expected": "NEGATIVE_FEEDBACK"
    },

    {
        "message": "Can you check the status of ticket 650932?",
        "expected": "QUERY"
    },
    {
        "message": "What is happening with ticket 123456?",
        "expected": "QUERY"
    },
    {
        "message": "Please give me an update on ticket 445566.",
        "expected": "QUERY"
    },
    {
        "message": "Is ticket 999888 resolved yet?",
        "expected": "QUERY"
    }
]


def evaluate_classifier():
    results = []

    correct = 0

    for case in TEST_CASES:
        actual = classify_message(case["message"])

        passed = actual == case["expected"]

        if passed:
            correct += 1

        results.append({
            "Message": case["message"],
            "Expected": case["expected"],
            "Actual": actual,
            "Passed": passed
        })

    total = len(TEST_CASES)

    accuracy = (
        (correct / total) * 100
        if total > 0
        else 0
    )

    return {
        "total": total,
        "correct": correct,
        "incorrect": total - correct,
        "accuracy": round(accuracy, 2),
        "results": results
    }