"""Reverse Jev: generate text one letter at a time by asking Jev to pick from a menu."""
import json, os, sys, urllib.request

MODEL = os.environ.get("JEV_MODEL", "~typesafe/jev-latest")
LETTERS = "etaoinshrdlcumwfgypbvkjxqz"  # most to least common in English
PAGE = 5
SPECIALS = [(" ", "space"), (".", "period"), (",", "comma"), ("\n", "newline"), (None, "END")]


def load_env():
    if os.path.exists(".env"):
        for line in open(".env"):
            k, _, v = line.strip().partition("=")
            if k and not k.startswith("#"):
                os.environ.setdefault(k, v.strip("'\""))


def ask(prompt):
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps({"model": MODEL, "max_tokens": 200,
                         "messages": [{"role": "user", "content": prompt}]}).encode(),
        headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
                 "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))["choices"][0]["message"]["content"] or ""


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
        opts = "\n".join(f"{'abcde'[i]}: {n!r}" for i, n in enumerate(names))
        prompt = (f"We are writing this together one character at a time. Goal: {goal}\n"
                  f"Text so far: {text!r}\n\nPick the next character:\n{opts}\n"
                  "f: none of these, show me more options\n"
                  "Reply with a single letter, a to f.")
        for _ in range(3):
            ans = ask(prompt).strip().lower()[:1]
            if ans in "abcdef" and ans:
                break
        else:
            ans = "f"
        if ans != "f":
            return chars['abcde'.index(ans)] if 'abcde'.index(ans) < len(chars) else ""
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
