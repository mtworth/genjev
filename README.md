# reverse-jev

A joke. Others have tried turning text models into decision models. This goes the other way:
a decision model (Jev, via OpenRouter's decisions endpoint) writes text one letter at a time by picking from a menu.

Each step Jev sees the text so far and picks a to e from five letters, ordered from most to
least common in English (etaoi, nshrd, ...). Option f shows the next five, looping back round.
After the last letter page comes a specials page: space, period, comma, newline, END.

    export OPENROUTER_API_KEY=...   # or put it in .env
    python3 reverse_jev.py "write one short sentence about a cat" 80
