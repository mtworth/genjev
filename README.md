# reverse-jev

A joke. Others have tried turning text models into decision models. This goes the other way:
a decision model (Jev, via OpenRouter's decisions endpoint) writes text one letter at a time by picking from a menu.

Each step Jev sees the question and the answer so far and picks one character from a single menu of all 42
options (letters, digits, space, period, comma, newline, END), shuffled each step (the cap is 255 options).
Set MODE=paged for the old five-at-a-time menu with a "more" option. The decision log prints at the end.

    export OPENROUTER_API_KEY=...   # or put it in .env
    python3 reverse_jev.py "write one short sentence about a cat" 80
