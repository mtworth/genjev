"""Reverse Jev: generate text one letter at a time by asking Jev to pick from a menu."""
import json, os, sys, urllib.request

MODEL = os.environ.get("JEV_MODEL", "~typesafe/jev-latest")  # a decisions model: /api/alpha/decisions, not chat
LETTERS = "etaoinshrdlcumwfgypbvkjxqz"  # most to least common in English
PAGE = 5
SPECIALS = [(" ", "space"), (".", "period"), (",", "comma"), ("\n", "newline"), (None, "END")]


def load_env():
    if os.path.exists(".env"):
        for line in open(".env"):
            k, _, v = line.strip().partition("=")
            if k and not k.startswith("#"):
                os.environ.setdefault(k, v.strip("'\""))


def decide(goal, text, criteria):
    body = {"model": MODEL,
            "questions": {"next": {"type": "choice", "criteria": criteria,
                                   "instructions": "We are writing text one character at a time. "
                                                   "Which option is the best next character?"}},
            "state": {"goal": goal, "text_so_far": text}}
    req = urllib.request.Request(
        "https://openrouter.ai/api/alpha/decisions", data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
                 "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))["answers"]["next"]["choice"]


def menu(page):
    """Page 0..n-1 cycles through the letters; the last page is the specials."""
    pages = [LETTERS[i:i + PAGE] for i in range(0, len(LETTERS), PAGE)]
    if page == len(pages):
        return [s for _, s in SPECIALS], [c for c, _ in SPECIALS], len(pages) + 1
    return list(pages[page]), list(pages[page]), len(pages) + 1


def pick(goal, text):
    page = 0
    while True:
        names, chars, npages = menu(page)
        criteria = {"abcde"[i]: f"the character {n!r}" for i, n in enumerate(names)}
        criteria["f"] = "none of these fit, show me more options"
        ans = decide(goal, text, criteria)
        if ans != "f":
            return chars["abcde".index(ans)]
        page = (page + 1) % npages


def main():
    load_env()
    goal = sys.argv[1] if len(sys.argv) > 1 else "write one short sentence about a cat"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    text = ""
    while len(text) < limit:
        c = pick(goal, text)
        if c is None:
            break
        text += c
        print(c, end="", flush=True)
    print()


if __name__ == "__main__":
    main()
