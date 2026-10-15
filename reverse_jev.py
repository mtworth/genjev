"""Reverse Jev: generate text one letter at a time by asking Jev to pick from a menu."""
import json, os, random, sys, urllib.request

MODEL = os.environ.get("JEV_MODEL", "~typesafe/jev-latest")  # a decisions model: /api/alpha/decisions, not chat
LETTERS = "abcdefghijklmnopqrstuvwxyz"
DIGITS = "0123456789"
PAGE = 5
ORDER = os.environ.get("ORDER", "alpha")  # alpha | reverse | shuffle, the order options are shown in
RNG = random.Random(int(os.environ.get("SEED", "0")))
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
                                   "instructions": "The answer is being written one character at a time. "
                                                   "What is the letter that would best continue the answer?"}},
            "state": {"question": goal, "answer_so_far": text}}
    req = urllib.request.Request(
        "https://openrouter.ai/api/alpha/decisions", data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
                 "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))["answers"]["next"]


def menu(page):
    """Pages cycle through letters a-z, digits 0-9, then specials. Returns (names, chars, n_pages)."""
    pages = [list(zip(LETTERS[i:i + PAGE], LETTERS[i:i + PAGE])) for i in range(0, len(LETTERS), PAGE)]
    pages += [list(zip(DIGITS[i:i + PAGE], DIGITS[i:i + PAGE])) for i in range(0, len(DIGITS), PAGE)]
    pages.append(SPECIALS)
    return [n for _, n in pages[page]], [c for c, _ in pages[page]], len(pages)


def pick(goal, text, log):
    page = 0
    while True:
        names, chars, npages = menu(page)
        pairs = list(zip(names, chars))
        if ORDER == "shuffle":
            RNG.shuffle(pairs)
        elif ORDER == "reverse":
            pairs.reverse()
        names, chars = [n for n, _ in pairs], [c for _, c in pairs]
        criteria = {"abcde"[i]: f"the character {n!r}" for i, n in enumerate(names)}
        criteria["f"] = "none of these fit, show me more options"
        ans = decide(goal, text, criteria)
        choice = ans["choice"]
        label = "more" if choice == "f" else repr(names["abcde".index(choice)])
        log.append((len(text), page + 1, names, ans["probabilities"], label, ans.get("confidence")))
        if choice != "f":
            return chars["abcde".index(choice)]
        page = (page + 1) % npages


def print_log(log):
    print(f"\n{'chars':>5} {'page':>4}  {'options':<28} {'probabilities a-f':<34} {'picked':<9} conf")
    for n, page, names, probs, label, conf in log:
        p = " ".join(f"{probs.get(k, 0):.2f}" for k in "abcdef")
        print(f"{n:>5} {page:>4}  {' '.join(names):<28} {p:<34} {label:<9} {conf}")


def main():
    load_env()
    goal = sys.argv[1] if len(sys.argv) > 1 else "write one short sentence about a cat"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    text, log = "", []
    while len(text) < limit:
        c = pick(goal, text, log)
        if c is None:
            break
        text += c
        print(c, end="", flush=True)
    print()
    print_log(log)
    json.dump(log, open(os.environ.get("LOG", "decision_log.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
