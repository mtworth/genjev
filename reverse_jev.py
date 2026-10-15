"""Reverse Jev: generate text one letter at a time by asking Jev to pick from a menu."""
import json, os, random, sys, urllib.request

MODEL = os.environ.get("JEV_MODEL", "~typesafe/jev-latest")  # a decisions model: /api/alpha/decisions, not chat
LETTERS = "abcdefghijklmnopqrstuvwxyz"
DIGITS = "0123456789"
PAGE = 5
MODE = os.environ.get("MODE", "flat")  # flat: every option in one question (cap is 255) | paged: five at a time
ORDER = os.environ.get("ORDER", "shuffle")  # alpha | reverse | shuffle, the order options are shown in
SAMPLE = os.environ.get("SAMPLE", "1") == "1"  # flat mode: draw from the probabilities instead of taking the top one
TEMP = float(os.environ.get("TEMP", "1"))  # below 1 sharpens the probabilities, above 1 flattens them
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


def top3(probs, names):
    best = sorted(probs, key=probs.get, reverse=True)[:3]
    return "  ".join(f"{names.get(k, k)!r} {probs[k]:.2f}" for k in best)


def pick_flat(goal, text, log):
    """One question with every character offered. The key is the character itself, so labels carry no order."""
    opts = [(c, c) for c in LETTERS + DIGITS] + [(n, c) for c, n in SPECIALS if c != " "] + [("space", " "), ("END", None)]
    if ORDER == "shuffle":
        RNG.shuffle(opts)
    elif ORDER == "reverse":
        opts.reverse()
    chars = dict(opts)
    ans = decide(goal, text, {k: f"the character {k!r}" for k, _ in opts})
    choice = ans["choice"]
    if SAMPLE:
        probs = ans["probabilities"]
        choice = RNG.choices(list(probs), weights=[p ** (1 / TEMP) for p in probs.values()])[0]
    log.append((len(text), len(opts), top3(ans["probabilities"], {}), choice, ans.get("confidence")))
    return chars[choice]


def pick_paged(goal, text, log):
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
        log.append((len(text), 6, top3(ans["probabilities"], dict(zip("abcde", names), f="more")), label, ans.get("confidence")))
        if choice != "f":
            return chars["abcde".index(choice)]
        page = (page + 1) % npages


def pick(goal, text, log):
    return (pick_flat if MODE == "flat" else pick_paged)(goal, text, log)


def print_log(log):
    print(f"\n{'chars':>5} {'shown':>5}  {'top three (probability)':<48} {'picked':<9} conf")
    for n, shown, top, label, conf in log:
        print(f"{n:>5} {shown:>5}  {top:<48} {label!r:<9} {conf}")


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
