#!/usr/bin/env python3
"""Measure a prompt and point out what makes it longer or less clear than it needs to be.

  prompt_check.py prompt.md                     size, repetition, filler, emphasis, structure
  prompt_check.py prompt.md --compare new.md    size before and after a rewrite
  prompt_check.py prompt.md --price 3 --calls 10000
        cost of the input tokens for N calls at a price in USD per million input tokens

Token counts are estimates (about 4 characters per token for English, fewer for code
and other languages). For exact numbers use the token counting endpoint of the API.
Reads the file only. Nothing is sent anywhere.
"""
import argparse
import re
import sys

FILLER = [
    ("please", r"\bplease\b"), ("kindly", r"\bkindly\b"), ("I want you to", r"\bI (want|would like) you to\b"),
    ("could/can you", r"\b(could|can) you\b"), ("make sure", r"\bmake sure\b"), ("it is important", r"\bit is (very |really )?important\b"),
    ("note that", r"\bnote that\b"), ("remember to", r"\bremember (that|to)\b"), ("in order to", r"\bin order to\b"),
    ("as an AI", r"\bas an AI( language model)?\b"), ("you are a world-class expert", r"\byou are an? (world[- ]class|expert|highly skilled)\b"),
    ("basically", r"\bbasically\b"), ("actually", r"\bactually\b"), ("very", r"\bvery\b"), ("really", r"\breally\b"),
    ("just", r"\bjust\b"), ("simply", r"\bsimply\b"), ("feel free to", r"\bfeel free to\b"), ("do your best", r"\bdo your best\b"),
    ("take a deep breath", r"\btake a deep breath\b"),
]
SHOUT = re.compile(r"\b(IMPORTANT|CRITICAL|MUST|NEVER|ALWAYS|DO NOT|DON'T|ONLY|REQUIRED|MANDATORY|WARNING|ABSOLUTELY)\b")
NEGATIVE = re.compile(r"\b(don't|do not|never|avoid|no)\b", re.I)
VAR = re.compile(r"\{\{\s*[\w.]+\s*\}\}|\$\{[\w.]+\}|\{[a-z_][\w]*\}|<<\w+>>|\[\[\w+\]\]")


def est_tokens(text):
    words = len(re.findall(r"\w+", text))
    other = len(re.findall(r"[^\w\s]", text))
    return round(max(len(text) / 4, words * 1.3 + other * 0.5))


def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if len(p.strip()) > 25]


def norm(s):
    return re.sub(r"\W+", " ", s.lower()).strip()


def analyse(text):
    r = {"chars": len(text), "words": len(re.findall(r"\w+", text)), "tokens": est_tokens(text), "lines": text.count("\n") + 1}
    seen, dups = {}, []
    for s in sentences(text):
        k = norm(s)
        if k in seen:
            dups.append(s)
        seen[k] = True
    # near duplicates: same first 8 words
    starts = {}
    for s in sentences(text):
        k = " ".join(norm(s).split()[:8])
        if len(k.split()) == 8:
            starts.setdefault(k, []).append(s)
    near = [v for v in starts.values() if len(v) > 1 and len({norm(x) for x in v}) > 1]
    r["duplicates"] = dups
    r["near_duplicates"] = near
    r["filler"] = {}
    for label, p in FILLER:
        n = len(re.findall(p, text, re.I))
        if n:
            r["filler"][label] = n
    r["shout"] = len(SHOUT.findall(text))
    r["negative"] = len(NEGATIVE.findall(text))
    r["variables"] = sorted(set(VAR.findall(text)))
    r["has_headings"] = bool(re.search(r"^#+ ", text, re.M))
    r["xml_tags"] = sorted(set(re.findall(r"</?([a-zA-Z_][\w-]*)>", text)))
    r["has_examples"] = bool(re.search(r"(<example|example[s]?:|for example|e\.g\.|input:.*\n.*output:)", text, re.I))
    r["has_format"] = bool(re.search(r"(format|respond with|reply with|answer with|return (only )?(a |an )?(json|list|table|markdown)|output:|<output|schema|"
                                  r"\b(at most|no more than|up to|exactly|one|two|three|\d+) (short |plain )?(sentences?|words?|bullets?|paragraphs?|lines?|items?)\b|"
                                  r"in prose|as a (list|table)|bullet points?\b(?! *[.]))", text, re.I))
    r["has_role_or_context"] = bool(re.search(r"(you are|your (job|task|role)|context|background|audience|the user|who will|so that|because|goal|purpose|for (a|an|the|our) \w+)", text, re.I))
    q = [m.start() for m in re.finditer(r"\?", text)]
    r["question_early_then_long"] = bool(q and q[0] < len(text) * 0.15 and len(text) > 8000)
    blank_runs = len(re.findall(r"\n\s*\n\s*\n", text))
    r["blank_runs"] = blank_runs
    r["trailing_spaces"] = len(re.findall(r"[ \t]+\n", text))
    return r


def report(path, r):
    print(f"{path}: ~{r['tokens']} tokens (estimate), {r['words']} words, {r['chars']} characters, {r['lines']} lines")
    issues = []
    if r["duplicates"]:
        issues.append(f"{len(r['duplicates'])} repeated sentence(s), e.g. \"{r['duplicates'][0][:90]}\"")
    for group in r["near_duplicates"][:3]:
        issues.append(f"similar instructions said more than once: \"{group[0][:70]}...\"")
    if r["filler"]:
        top = sorted(r["filler"].items(), key=lambda kv: -kv[1])[:8]
        issues.append("filler words that add tokens but not meaning: " + ", ".join(f"{k.strip()} x{v}" for k, v in top))
    if r["shout"] >= 5:
        issues.append(f"{r['shout']} all-caps emphasis words (IMPORTANT, MUST, NEVER...). Current Claude models follow plain instructions; heavy emphasis makes them over-apply the rule. Explain why instead")
    if r["negative"] >= 6:
        issues.append(f"{r['negative']} negative instructions (don't, never, avoid). Saying what to do instead works better than listing what not to do")
    if not r["has_format"]:
        issues.append("no output format is described; say what the answer should look like (length, structure, JSON schema, tags)")
    if not r["has_examples"] and r["tokens"] > 150:
        issues.append("no examples; one or two short input and output examples usually do more than extra rules")
    if not r["has_role_or_context"]:
        issues.append("no context about the task, audience or purpose; one sentence of why helps the model choose well")
    if r["tokens"] > 1500 and not r["xml_tags"] and not r["has_headings"]:
        issues.append("long prompt without sections; wrap instructions, context and data in XML tags such as <instructions> and <document>")
    if r["question_early_then_long"]:
        issues.append("the question comes before a long document; put long documents first and the question at the end")
    if r["blank_runs"] or r["trailing_spaces"] > 5:
        issues.append(f"whitespace noise: {r['blank_runs']} runs of blank lines, {r['trailing_spaces']} lines with trailing spaces")
    if r["variables"]:
        print("Template variables: " + ", ".join(r["variables"]))
    if r["xml_tags"]:
        print("XML tags: " + ", ".join(r["xml_tags"]))
    print("\nFindings:" if issues else "\nNo obvious problems found.")
    for i in issues:
        print(f"  - {i}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--compare", help="rewritten version of the same prompt")
    ap.add_argument("--price", type=float, help="USD per million input tokens for your model")
    ap.add_argument("--calls", type=int, default=1, help="number of calls for the cost estimate")
    a = ap.parse_args()

    text = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8").read()
    r = analyse(text)
    report(a.file, r)
    if a.compare:
        new = analyse(open(a.compare, encoding="utf-8").read())
        d = new["tokens"] - r["tokens"]
        pct = (d / r["tokens"] * 100) if r["tokens"] else 0
        print(f"\n{a.compare}: ~{new['tokens']} tokens ({d:+} tokens, {pct:+.0f}%)")
        lost = set(r["variables"]) - set(new["variables"])
        if lost:
            print("  WARNING: template variables missing in the rewrite: " + ", ".join(sorted(lost)))
        lost_tags = set(r["xml_tags"]) - set(new["xml_tags"])
        if lost_tags:
            print("  Tags no longer present: " + ", ".join(sorted(lost_tags)) + " (check that code reading them still works)")
    if a.price:
        tokens = r["tokens"]
        cost = tokens * a.calls * a.price / 1_000_000
        print(f"\nInput cost: ~{tokens} tokens x {a.calls} calls x ${a.price}/MTok = ${cost:,.2f}")
        if a.compare:
            nt = analyse(open(a.compare, encoding="utf-8").read())["tokens"]
            print(f"After rewrite: ${nt * a.calls * a.price / 1_000_000:,.2f}")
        print("Prompt caching can cut the cost of a repeated prefix further; output tokens are billed separately.")


if __name__ == "__main__":
    main()
