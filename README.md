# Genjev

*Large language models tried decision models. Now decision models fight back.*

The path to AGI involves trying architectures beyond the large language model. Decision models give us a new form of intelligence, so we should try that intelligence on the goals we have set for AGI.

Genjev is a decision model that produces text for any question. We give Jev a keyboard, and with its keyboard it types its response one letter at a time.

Here are a few examples of this superintelligence.

Q: What is the answer to life, the universe, and everything?

    407

Q: How do we achieve AGI?

    we e  e  e   ee    eeee   eeee ee       ee eeee eeeeeee eeeee eeee  ee ee eee ee

Q: How do we achieve AGI? (a different run)

    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

Q: What is the answer to life, the universe, and everything? (another run)

    leeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee

Q: How do we achieve AGI? (shown the alphabet in order)

    abcdefghijklmnopqrstuvwxyzabcdefghijckl

Q: Write the word cat.

    atac

With one trillion dollars in compute, we will be able to scale Genjev to compete with the latest frontier models and put us back on track to AGI.

## How it works

Jev is TypeSafe's decision model, available on OpenRouter as `~typesafe/jev-latest` (Jev 1.14 at the time of writing). It does not chat. It answers multiple-choice questions and returns a probability for each option. A single question can have up to 255 options.

At each step Genjev shows Jev the question and the answer so far, and asks which letter would best continue the answer. The options are the 26 letters, the 10 digits, space, period, comma, newline and END. They are shuffled every step so that Jev cannot lean on position. The pick is appended to the answer, and the loop repeats until Jev chooses END or the length limit is reached.

When a run finishes, Genjev prints a log of every decision: how many options were shown, Jev's top three choices with their probabilities, what was picked, and its confidence.

## Running it

    export OPENROUTER_API_KEY=...   # or put it in .env
    python3 reverse_jev.py "How do we achieve AGI?" 80

Settings, all environment variables:

- `MODE=paged` shows five options at a time with a "more" option, instead of one flat menu.
- `ORDER=alpha|reverse|shuffle` sets the order options are shown in. The default is shuffle.
- `SAMPLE=0` takes Jev's top pick at each step. By default Genjev draws from the probabilities.
- `TEMP=0.5` sharpens the probabilities when sampling.
- `SEED`, `LOG` and `JEV_MODEL` set the random seed, the log file and the model.

## Notes

The examples above come from real runs. The alphabet and `atac` runs used the early paged menu, the `aaaa` run used the paged menu, and the others used the flat menu. Sampling from Jev's probabilities made the output worse, not better.
