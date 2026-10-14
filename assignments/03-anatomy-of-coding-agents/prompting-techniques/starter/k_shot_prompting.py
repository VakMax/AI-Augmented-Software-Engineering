"""K-shot prompting — ticket classification.

Task: classify a customer message into one of: billing, shipping, returns,
technical, other. Use in-context EXAMPLES (k-shot) so the model outputs exactly the
label, lowercase, with no extra text.

Only edit YOUR_SYSTEM_PROMPT.
Run:  python k_shot_prompting.py
"""
from ollama import chat

MODEL = "llama3.1:8b"
NUM_RUNS = 5

# TODO: Fill this in! Include a few labeled examples (k-shot) in the system prompt.
YOUR_SYSTEM_PROMPT = """
Classify customer support messages using exactly one label:
billing, shipping, returns, technical, or other.

billing: payment problems, charges, or invoices.
shipping: delivery status, delays, or missing packages.
returns: sending products back, exchanges, or product refunds.
technical: errors or problems using the website or app.
other: messages that do not fit those categories.

Examples:
Message: I paid once, but my bank shows two payments.
Label: billing

Message: The tracking number has not updated since Monday.
Label: shipping

Message: These pants do not fit. How can I exchange them?
Label: returns

Message: The checkout page freezes when I click Pay.
Label: technical

Message: What time does your store open?
Label: other

Return only the lowercase label. Do not include an explanation,
punctuation, or the word "Label".
"""

CASES = [
    ("My card was charged twice for order 4412.", "billing"),
    ("Where is my package? It's been two weeks.", "shipping"),
    ("I want to send the shoes back for a refund.", "returns"),
    ("The app crashes every time I open my cart.", "technical"),
]


def classify(system_prompt: str, message: str) -> str:
    resp = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ],
        options={"temperature": 0.0},
    )
    return resp.message.content.strip().lower()


def run() -> bool:
    passed = 0
    for message, expected in CASES:
        got = classify(YOUR_SYSTEM_PROMPT, message)
        ok = got == expected
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] {message!r} -> got {got!r}, expected {expected!r}")
    print(f"{passed}/{len(CASES)} correct")
    return passed == len(CASES)


if __name__ == "__main__":
    run()
