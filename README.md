# reverse-jev

A joke. Others have tried turning text models into decision models. This goes the other way:
a decision model (Jev, via OpenRouter's decisions endpoint) writes text one letter at a time by picking from a menu.

Each step Jev sees the text so far and picks a to e from five characters: letters a-z in order,
then digits 0-9, then specials (space, period, comma, newline, END). Option f shows the next five, looping round.

    export OPENROUTER_API_KEY=...   # or put it in .env
    python3 reverse_jev.py "write one short sentence about a cat" 80
